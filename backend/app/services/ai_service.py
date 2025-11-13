"""
AI Service for NLP and ML Processing using Google Gemini
"""
import google.generativeai as genai
from app.core.config import settings
import json
import re
from datetime import datetime

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use gemini-2.5-flash for fast, high-quality responses
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
    
    async def analyze_contract(self, text: str) -> dict:
        """Analyze contract text and extract structured data"""
        if not self.model:
            # Fallback to basic extraction if Gemini not configured
            return self._basic_contract_extraction(text)
        
        prompt = f"""
        Analyze the following contract and extract structured information. Return ONLY a valid JSON object with:
        - title: Contract title
        - contract_number: Contract number if present
        - type: Type of contract (supplier, customer, partnership, employment, nda, other)
        - party_a: First party name
        - party_b: Second party name
        - effective_date: Effective date (ISO format or null)
        - expiration_date: Expiration date (ISO format or null)
        - renewal_date: Renewal date (ISO format or null)
        - contract_value: Monetary value if present
        - clauses: Array of clause objects with type, text, and data
        - risk_score: Risk score 0-100
        - risk_factors: Array of risk factor strings
        - risks: Array of risk objects with type, severity, description, mitigation
        - tags: Array of relevant tags
        
        Contract text:
        {text[:8000]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Extract JSON from response - try multiple patterns
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    # Ensure dates are strings for now (will be parsed later)
                    return parsed
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    json_str = json_match.group()
                    json_str = json_str.replace("'", '"')  # Replace single quotes
                    try:
                        return json.loads(json_str)
                    except:
                        pass
        except Exception as e:
            print(f"AI analysis error: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback to basic extraction
        return self._basic_contract_extraction(text)
    
    def _basic_contract_extraction(self, text: str) -> dict:
        """Basic contract extraction without AI"""
        # Simple regex-based extraction
        title_match = re.search(r'(?:Contract|Agreement|Contract for|Agreement for|SERVICE AGREEMENT)\s+([^\n]+)', text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else text.split('\n')[0][:100] or "Untitled Contract"
        
        # Extract contract number
        contract_num_match = re.search(r'Contract Number[:\s]+([A-Z0-9-]+)', text, re.IGNORECASE)
        contract_number = contract_num_match.group(1) if contract_num_match else None
        
        # Extract party names - try multiple patterns
        party_a = None
        party_b = None
        
        # Pattern 1: "Party A: ..." or "Party A:" - extract full company name
        party_a_match = re.search(r'Party A[:\s]+([^\n]+?)(?:,|\.|$)', text, re.IGNORECASE)
        if party_a_match:
            party_a = party_a_match.group(1).strip()
            # Clean up - remove "a corporation organized..." etc.
            party_a = re.sub(r',\s*a\s+[^,]+', '', party_a, flags=re.IGNORECASE).strip()
            party_b_match = re.search(r'Party B[:\s]+([^\n]+?)(?:,|\.|$)', text, re.IGNORECASE)
            if party_b_match:
                party_b = party_b_match.group(1).strip()
                party_b = re.sub(r',\s*a\s+[^,]+', '', party_b, flags=re.IGNORECASE).strip()
        
        # Pattern 2: "between X and Y"
        if not party_a:
            between_match = re.search(r'between[:\s]+([^,\n]+?)[,\s]+and[:\s]+([^\n]+)', text, re.IGNORECASE)
            if between_match:
                party_a = between_match.group(1).strip()
                party_b = between_match.group(2).strip()
        
        # Pattern 3: Look for company names after "PARTIES:" section
        if not party_a:
            parties_section = re.search(r'PARTIES[:\s]+(.*?)(?:\n\n|\nSERVICES|\nCONTRACT)', text, re.IGNORECASE | re.DOTALL)
            if parties_section:
                parties_text = parties_section.group(1)
                # Look for company names (capitalized words, Inc., LLC, etc.)
                companies = re.findall(r'([A-Z][A-Za-z\s]+(?:Inc\.|LLC|Corp\.|Ltd\.|Solutions|Services))', parties_text)
                if len(companies) >= 2:
                    party_a = companies[0].strip()
                    party_b = companies[1].strip()
                elif len(companies) == 1:
                    party_a = companies[0].strip()
                    # Try to find second party
                    remaining = parties_text.replace(companies[0], '', 1)
                    second_company = re.search(r'([A-Z][A-Za-z\s]+(?:Inc\.|LLC|Corp\.|Ltd\.|Solutions|Services))', remaining)
                    if second_company:
                        party_b = second_company.group(1).strip()
        
        # Default if nothing found
        if not party_a:
            party_a = "Party A"
        if not party_b:
            party_b = "Party B"
        
        # Extract dates (various formats)
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract monetary values
        money_pattern = r'\$?([\d,]+\.?\d*)\s*(?:USD|dollars?|EUR|GBP)'
        money_matches = re.findall(money_pattern, text, re.IGNORECASE)
        contract_value = float(money_matches[0].replace(',', '')) if money_matches else None
        
        # Extract risk factors
        risk_factors = []
        if 'risk' in text.lower() or 'penalty' in text.lower():
            risk_factors.append("Contains risk clauses")
        if 'compliance' in text.lower() or 'gdpr' in text.lower():
            risk_factors.append("Compliance requirements")
        
        return {
            "title": title,
            "contract_number": contract_number,
            "type": "other",
            "party_a": party_a,
            "party_b": party_b,
            "effective_date": dates[0] if dates else None,
            "expiration_date": dates[1] if len(dates) > 1 else None,
            "renewal_date": dates[2] if len(dates) > 2 else None,
            "contract_value": contract_value,
            "clauses": [],
            "risk_score": 50.0,
            "risk_factors": risk_factors,
            "risks": [],
            "tags": []
        }
    
    async def generate_report_summary(self, data: dict, report_type: str) -> str:
        """Generate natural language summary for reports"""
        if not self.model:
            return "Report generated successfully."
        
        prompt = f"""
        Generate a concise executive summary (2-3 paragraphs) for a {report_type} report based on the following data:
        {json.dumps(data, indent=2)[:4000]}
        
        Make it CFO-ready and highlight key insights.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Report summary generation error: {e}")
            return "Report generated successfully."

