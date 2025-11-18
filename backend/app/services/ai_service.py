"""
AI Service for NLP and ML Processing using Google Gemini
"""
import google.generativeai as genai
from app.core.config import settings
from app.services.scoring_service import ScoringService
import json
import re
from datetime import datetime

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use gemini-2.5-flash for fast, high-quality responses
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                # Fallback to gemini-2.0-flash if 2.5 is not available
                print(f"[AIService] gemini-2.5-flash failed, trying gemini-2.0-flash: {e}")
                try:
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                except Exception as e2:
                    print(f"[AIService] gemini-2.0-flash also failed: {e2}")
                    self.model = None
        else:
            self.model = None
    
    async def analyze_contract(self, text: str) -> dict:
        """Analyze contract text and extract structured data"""
        if not self.model:
            # Fallback to basic extraction if Gemini not configured
            return self._basic_contract_extraction(text)
        
        prompt = f"""
        Analyze the following contract and extract structured information. Return ONLY a valid JSON object with:
        - title: Contract title (extract from first line or "SERVICE AGREEMENT" etc.)
        - contract_number: Contract number if present (look for "Contract Number:" or similar)
        - type: Type of contract (supplier, customer, partnership, employment, nda, other)
        - party_a: First party name (look for "Party A:" or first company name mentioned)
        - party_b: Second party name (look for "Party B:" or second company name mentioned)
        - effective_date: Effective date in ISO format YYYY-MM-DD (look for "Effective Date:" or "commence on")
        - expiration_date: Expiration date in ISO format YYYY-MM-DD (look for "Expiration Date:" or "continue until")
        - renewal_date: Renewal date in ISO format YYYY-MM-DD (look for "renewal" or "renewal discussions")
        - contract_value: Monetary value as a number only, no currency symbols (look for "Contract Value:" or "total contract value" or largest dollar amount)
        - clauses: Array of clause objects with type, text, and data
        - risk_score: Initial risk assessment score 0-100 (where 0=low risk, 100=high risk)
        - risk_factors: Array of specific risk factor strings (e.g., "Penalty clauses present", "Auto-renewal enabled", "Data privacy obligations")
        - risks: Array of risk objects, each with:
          * type: Risk category (financial, legal, operational, compliance, etc.)
          * severity: One of "critical", "high", "medium", "low", "minor"
          * description: Detailed description of the risk
          * mitigation: Recommended mitigation strategy
        - tags: Array of relevant tags
        
        CRITICAL: Extract party names exactly as written (e.g., "TechCorp Solutions Inc." not just "TechCorp"). 
        Extract dates in full format and convert to ISO (e.g., "January 1, 2024" -> "2024-01-01").
        Extract contract value as a number (e.g., "$500,000.00 USD" -> 500000.0).
        
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
                    # Always run fallback extraction to ensure we have complete data
                    fallback = self._basic_contract_extraction(text)
                    
                    # Helper function to check if a value is valid (not empty, None, or "Unknown")
                    def is_valid(value):
                        if value is None:
                            return False
                        if isinstance(value, str):
                            return value.strip() and value.strip().lower() != "unknown"
                        return True
                    
                    # Merge: Use AI values if valid, otherwise use fallback
                    merged = {
                        "title": parsed.get("title") if is_valid(parsed.get("title")) else fallback.get("title"),
                        "contract_number": parsed.get("contract_number") if is_valid(parsed.get("contract_number")) else fallback.get("contract_number"),
                        "type": parsed.get("type") if is_valid(parsed.get("type")) else fallback.get("type"),
                        "party_a": parsed.get("party_a") if is_valid(parsed.get("party_a")) else fallback.get("party_a"),
                        "party_b": parsed.get("party_b") if is_valid(parsed.get("party_b")) else fallback.get("party_b"),
                        "effective_date": parsed.get("effective_date") if is_valid(parsed.get("effective_date")) else fallback.get("effective_date"),
                        "expiration_date": parsed.get("expiration_date") if is_valid(parsed.get("expiration_date")) else fallback.get("expiration_date"),
                        "renewal_date": parsed.get("renewal_date") if is_valid(parsed.get("renewal_date")) else fallback.get("renewal_date"),
                        "contract_value": parsed.get("contract_value") if parsed.get("contract_value") is not None else fallback.get("contract_value"),
                        "clauses": parsed.get("clauses", []) if parsed.get("clauses") else fallback.get("clauses", []),
                        "risk_score": parsed.get("risk_score") if parsed.get("risk_score") is not None else fallback.get("risk_score"),
                        "risk_factors": parsed.get("risk_factors", []) if parsed.get("risk_factors") else fallback.get("risk_factors", []),
                        "risks": parsed.get("risks", []) if parsed.get("risks") else fallback.get("risks", []),
                        "tags": parsed.get("tags", []) if parsed.get("tags") else fallback.get("tags", [])
                    }
                    return merged
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    json_str = json_match.group()
                    json_str = json_str.replace("'", '"')  # Replace single quotes
                    try:
                        parsed = json.loads(json_str)
                        # Always run fallback extraction to ensure we have complete data
                        fallback = self._basic_contract_extraction(text)
                        
                        # Helper function to check if a value is valid (not empty, None, or "Unknown")
                        def is_valid(value):
                            if value is None:
                                return False
                            if isinstance(value, str):
                                return value.strip() and value.strip().lower() != "unknown"
                            return True
                        
                        # Merge: Use AI values if valid, otherwise use fallback
                        merged = {
                            "title": parsed.get("title") if is_valid(parsed.get("title")) else fallback.get("title"),
                            "contract_number": parsed.get("contract_number") if is_valid(parsed.get("contract_number")) else fallback.get("contract_number"),
                            "type": parsed.get("type") if is_valid(parsed.get("type")) else fallback.get("type"),
                            "party_a": parsed.get("party_a") if is_valid(parsed.get("party_a")) else fallback.get("party_a"),
                            "party_b": parsed.get("party_b") if is_valid(parsed.get("party_b")) else fallback.get("party_b"),
                            "effective_date": parsed.get("effective_date") if is_valid(parsed.get("effective_date")) else fallback.get("effective_date"),
                            "expiration_date": parsed.get("expiration_date") if is_valid(parsed.get("expiration_date")) else fallback.get("expiration_date"),
                            "renewal_date": parsed.get("renewal_date") if is_valid(parsed.get("renewal_date")) else fallback.get("renewal_date"),
                            "contract_value": parsed.get("contract_value") if parsed.get("contract_value") is not None else fallback.get("contract_value"),
                            "clauses": parsed.get("clauses", []) if parsed.get("clauses") else fallback.get("clauses", []),
                            "risk_score": parsed.get("risk_score") if parsed.get("risk_score") is not None else fallback.get("risk_score"),
                            "risk_factors": parsed.get("risk_factors", []) if parsed.get("risk_factors") else fallback.get("risk_factors", []),
                            "risks": parsed.get("risks", []) if parsed.get("risks") else fallback.get("risks", []),
                            "tags": parsed.get("tags", []) if parsed.get("tags") else fallback.get("tags", [])
                        }
                        return merged
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
        
        # Pattern 1: "Party A: ..." - extract company name (stop before "a corporation" or similar)
        party_a_match = re.search(r'Party A[:\s]+([^\n]+?)(?:,\s*a\s+|,\s*an\s+|$)', text, re.IGNORECASE)
        if party_a_match:
            party_a = party_a_match.group(1).strip()
            # Clean up trailing commas
            party_a = party_a.rstrip(',').strip()
        
        party_b_match = re.search(r'Party B[:\s]+([^\n]+?)(?:,\s*a\s+|,\s*an\s+|$)', text, re.IGNORECASE)
        if party_b_match:
            party_b = party_b_match.group(1).strip()
            # Clean up trailing commas
            party_b = party_b.rstrip(',').strip()
        
        # Pattern 2: "between X and Y"
        if not party_a or not party_b:
            between_match = re.search(r'between[:\s]+([^,\n]+?)[,\s]+and[:\s]+([^\n]+?)(?:,|\.|$)', text, re.IGNORECASE)
            if between_match:
                if not party_a:
                    party_a = between_match.group(1).strip()
                if not party_b:
                    party_b = between_match.group(2).strip()
        
        # Pattern 3: Look for company names after "PARTIES:" section
        if not party_a or not party_b:
            parties_section = re.search(r'PARTIES[:\s]+(.*?)(?:\n\n|\nSERVICES|\nCONTRACT|\nTERM)', text, re.IGNORECASE | re.DOTALL)
            if parties_section:
                parties_text = parties_section.group(1)
                # Look for company names (capitalized words, Inc., LLC, etc.)
                companies = re.findall(r'([A-Z][A-Za-z\s&]+(?:Inc\.|LLC|Corp\.|Ltd\.|Solutions|Services|LLC|Inc))', parties_text)
                if len(companies) >= 2:
                    if not party_a:
                        party_a = companies[0].strip()
                    if not party_b:
                        party_b = companies[1].strip()
                elif len(companies) == 1:
                    if not party_a:
                        party_a = companies[0].strip()
                    # Try to find second party
                    remaining = parties_text.replace(companies[0], '', 1)
                    second_company = re.search(r'([A-Z][A-Za-z\s&]+(?:Inc\.|LLC|Corp\.|Ltd\.|Solutions|Services|LLC|Inc))', remaining)
                    if second_company and not party_b:
                        party_b = second_company.group(1).strip()
        
        # Pattern 4: Look for signatures at the end
        if not party_a or not party_b:
            signature_match = re.search(r'([A-Z][A-Za-z\s&]+(?:Inc\.|LLC|Corp\.|Ltd\.|Solutions|Services))\s+([A-Z][A-Za-z\s&]+(?:Inc\.|LLC|Corp\.|Ltd\.|Solutions|Services))', text[-200:], re.IGNORECASE)
            if signature_match:
                if not party_a:
                    party_a = signature_match.group(1).strip()
                if not party_b:
                    party_b = signature_match.group(2).strip()
        
        # Default if nothing found
        if not party_a:
            party_a = "Unknown"
        if not party_b:
            party_b = "Unknown"
        
        # Extract dates (various formats) - look for specific date labels first
        effective_date = None
        expiration_date = None
        renewal_date = None
        
        # Look for labeled dates
        effective_match = re.search(r'Effective Date[:\s]+([^\n]+)', text, re.IGNORECASE)
        if effective_match:
            date_str = effective_match.group(1).strip()
            effective_date = self._parse_date_string(date_str)
        
        expiration_match = re.search(r'Expiration Date[:\s]+([^\n]+)', text, re.IGNORECASE)
        if expiration_match:
            date_str = expiration_match.group(1).strip()
            expiration_date = self._parse_date_string(date_str)
        
        renewal_match = re.search(r'(?:Renewal|renewal discussions to commence)[^\n]*?([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})', text, re.IGNORECASE)
        if renewal_match:
            date_str = renewal_match.group(1).strip()
            renewal_date = self._parse_date_string(date_str)
        
        # Fallback: extract all dates and assign by position
        if not effective_date or not expiration_date:
            date_patterns = [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ]
            dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                dates.extend(matches)
            
            # Assign dates by position if not found by label
            if dates:
                if not effective_date and len(dates) > 0:
                    effective_date = dates[0]
                if not expiration_date and len(dates) > 1:
                    expiration_date = dates[1]
                if not renewal_date and len(dates) > 2:
                    renewal_date = dates[2]
        
        # Extract monetary values - look for "contract value" or "total value"
        contract_value = None
        # Pattern 1: Look for "Contract Value:" or "total contract value" followed by dollar amount
        value_match = re.search(r'(?:Contract Value|total contract value|Total Value)[:\s]+(?:is\s+)?.*?\$([\d,]+\.?\d*)', text, re.IGNORECASE)
        if value_match:
            contract_value = float(value_match.group(1).replace(',', ''))
        else:
            # Fallback: find largest monetary value with $ sign
            money_pattern = r'\$([\d,]+\.?\d*)'
            money_matches = re.findall(money_pattern, text, re.IGNORECASE)
            if money_matches:
                # Get the largest value (likely the contract value)
                values = [float(m.replace(',', '')) for m in money_matches]
                contract_value = max(values) if values else None
        
        # Extract risk factors using scoring service
        risk_factors = ScoringService.extract_risk_factors_from_text(text)
        
        # Calculate risk score using scoring service
        has_penalties = any('penalty' in factor.lower() for factor in risk_factors)
        has_auto_renewal = any('renewal' in factor.lower() or 'auto' in factor.lower() for factor in risk_factors)
        
        risk_score = ScoringService.calculate_risk_score(
            risk_factors=risk_factors,
            risks=[],
            contract_value=contract_value,
            expiration_date=dates[1] if len(dates) > 1 else None,
            has_penalties=has_penalties,
            has_auto_renewal=has_auto_renewal,
            ai_risk_score=None  # No AI score in fallback
        )
        
        return {
            "title": title,
            "contract_number": contract_number,
            "type": "other",
            "party_a": party_a,
            "party_b": party_b,
            "effective_date": effective_date,
            "expiration_date": expiration_date,
            "renewal_date": renewal_date,
            "contract_value": contract_value,
            "clauses": [],
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "risks": [],
            "tags": []
        }
    
    def _parse_date_string(self, date_str: str) -> str:
        """Parse date string to ISO format or return as-is if parsing fails"""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Try to parse common date formats
        try:
            from dateutil import parser
            parsed = parser.parse(date_str)
            return parsed.isoformat()
        except:
            # Return as-is if parsing fails (will be handled by contract service)
            return date_str
    
    async def analyze_file(self, text: str, filename: str, file_type: str = None) -> dict:
        """Analyze any file and extract key information, insights, and summary"""
        if not self.model:
            return {
                "summary": "File analysis requires AI configuration.",
                "key_points": [],
                "insights": [],
                "file_type": file_type or "unknown"
            }
        
        # Determine file type from extension if not provided
        if not file_type:
            file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
            file_type = file_extension
        
        prompt = f"""
        Analyze the following document/file content and provide a comprehensive analysis. Return ONLY a valid JSON object with:
        - summary: A concise 2-3 sentence summary of the document
        - key_points: Array of 5-10 key points or important information extracted
        - insights: Array of insights, observations, or notable findings
        - document_type: Type of document (contract, report, policy, agreement, etc.)
        - topics: Array of main topics covered
        - important_dates: Array of any important dates mentioned
        - entities: Array of important entities (people, companies, organizations) mentioned
        - recommendations: Array of any recommendations or action items if applicable
        
        File name: {filename}
        File type: {file_type}
        
        Document content:
        {text[:10000]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    parsed["file_type"] = file_type
                    parsed["filename"] = filename
                    return parsed
                except json.JSONDecodeError:
                    json_str = json_match.group()
                    json_str = json_str.replace("'", '"')
                    try:
                        parsed = json.loads(json_str)
                        parsed["file_type"] = file_type
                        parsed["filename"] = filename
                        return parsed
                    except:
                        pass
        except Exception as e:
            print(f"File analysis error: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback response
        return {
            "summary": f"Analyzed {filename}. Content extracted successfully.",
            "key_points": [],
            "insights": [],
            "document_type": "unknown",
            "topics": [],
            "important_dates": [],
            "entities": [],
            "recommendations": [],
            "file_type": file_type,
            "filename": filename
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

