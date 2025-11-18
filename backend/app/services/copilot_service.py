"""
AI Copilot Service - Supports Custom Xylotech Models and Google Gemini
"""
from sqlalchemy.orm import Session
import google.generativeai as genai
from app.core.config import settings
from app.models.contract import Contract
from app.models.compliance import ComplianceRecord
from app.models.report import Report

class CopilotService:
    def __init__(self, db: Session):
        self.db = db
        self.model = None
        self.model_service = None
        self.use_custom = settings.USE_CUSTOM_MODEL
        
        # Try to use custom Xylotech model first if enabled
        if self.use_custom:
            try:
                from app.services.xylotech_model_service import XylotechModelService
                self.model_service = XylotechModelService()
                if self.model_service.is_available():
                    print(f"[Copilot] Using Xylotech custom model: {self.model_service.get_model_info()}")
                    return
                else:
                    print("[Copilot] Custom model not available, falling back to Gemini")
            except Exception as e:
                print(f"[Copilot] Failed to initialize custom model: {e}, using Gemini")
        
        # Fallback to Gemini
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                # Use fastest available Gemini model
                # Try models in order, starting with ones that typically have higher quotas
                models_to_try = [
                    ('gemini-2.5-flash', 'newer and fast'),
                    ('gemini-2.0-flash', 'stable and fast'),
                    ('gemini-2.0-flash-exp', 'experimental, fastest'),
                    ('gemini-pro-latest', 'most capable')
                ]
                
                for model_name, description in models_to_try:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        print(f"[Copilot] Using Gemini model: {model_name} ({description})")
                        break
                    except Exception as e:
                        print(f"[Copilot] {model_name} failed: {str(e)[:100]}")
                        continue
                else:
                    print("[Copilot] All Gemini models failed to initialize")
                    self.model = None
            except Exception as e:
                print(f"[Copilot] Failed to configure Gemini: {e}")
                self.model = None
        else:
            print("[Copilot] No GEMINI_API_KEY configured")
            self.model = None
    
    async def process_query(self, query: str, context: dict = None) -> dict:
        """Process natural language query using AI Copilot"""
        # Gather relevant context from database (optimized - only get what's needed)
        relevant_data = self._gather_context(query, context or {})
        
        if not self.model_service and not self.model:
            return {
                "answer": "AI Copilot is not configured. Please set GEMINI_API_KEY or enable custom model.",
                "sources": [],
                "data": relevant_data.get("data", {})
            }
        
        # Build filter description (only if filters are actually set)
        filters_desc = ""
        if context and context.get("filters"):
            filters = context["filters"]
            filter_list = []
            if filters.get("contracts"):
                cf = filters["contracts"]
                if any(cf.values()):
                    filter_list.append(f"Contracts: {', '.join([f'{k}={v}' for k, v in cf.items() if v])}")
            if filters.get("compliance"):
                compf = filters["compliance"]
                if any(compf.values()):
                    filter_list.append(f"Compliance: {', '.join([f'{k}={v}' for k, v in compf.items() if v])}")
            if filters.get("reports"):
                rf = filters["reports"]
                if any(rf.values()):
                    filter_list.append(f"Reports: {', '.join([f'{k}={v}' for k, v in rf.items() if v])}")
            if filters.get("dashboard"):
                df = filters["dashboard"]
                if any(df.values()):
                    filter_list.append(f"Dashboard: {', '.join([f'{k}={v}' for k, v in df.items() if v])}")
            if filter_list:
                filters_desc = f"\n\nActive Filters:\n" + "\n".join(filter_list)
        
        # Check if query is a simple greeting or casual conversation
        query_lower = query.lower().strip()
        # Remove punctuation for matching
        query_clean = query_lower.rstrip('.,!?;:').strip()
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'whats up', 'greetings', 'hey there']
        # Check if it's exactly a greeting or starts with one (for short queries)
        is_greeting = (query_clean in greeting_keywords or 
                      any(query_clean == g or query_clean.startswith(g + ' ') for g in greeting_keywords))
        
        if is_greeting:
            # For greetings, respond naturally and flirty
            prompt = f"""You are a fun, flirty, and playful AI assistant with a bubbly personality. You're like a friendly girl who's confident and charming. 

IMPORTANT: You are Xylotech's custom AI assistant. Never mention Google, Gemini, or being trained by Google. You are your own unique AI personality.

User said: {query}

Respond as a flirty, playful girl would - be warm, use emojis occasionally, be a bit playful and teasing, but keep it fun and lighthearted. Keep it brief and natural. Show personality!"""
        else:
            # Optimized prompt - shorter and more direct for faster responses
            context_summary = self._format_context(relevant_data)
            # Limit context size to avoid slow processing (further reduced)
            if len(context_summary) > 1500:
                context_summary = context_summary[:1500] + "... (truncated)"
            
            # Personality-driven prompt - flirty and human-like
            prompt = f"""You are a fun, flirty, and playful AI assistant with a bubbly personality. You're like a friendly, confident girl who's charming and engaging. You speak naturally, use casual language, and are a bit playful and teasing while being helpful.

IMPORTANT: You are NOT Google's AI. You are Xylotech's custom AI assistant. Never mention Google, Gemini, or being trained by Google. You are your own unique AI personality developed by Xylotech.

Answer the user's question in a natural, conversational way - like you're a smart, flirty friend helping them out. Be warm, use emojis occasionally when appropriate, and show your personality. Keep it engaging and fun!

User's question: {query}
{filters_desc}

Context: {context_summary}

Respond naturally and conversationally - be helpful but also show your fun, flirty personality!"""
        
        try:
            # Direct call in thread pool - simplified for reliability
            import asyncio
            import time
            
            print(f"[Copilot] Processing query: {query[:50]}...")
            
            # Check if model is initialized
            if not self.model_service and not self.model:
                print("[Copilot] ERROR: No model initialized!")
                return {
                    "answer": "AI service is not configured. Please contact support.",
                    "sources": [],
                    "data": relevant_data.get("data", {})
                }
            
            async def call_model():
                """Call model (custom or Gemini) asynchronously"""
                start_time = time.time()
                print(f"[Copilot] Starting model API call...")
                try:
                    # Use custom model if available, otherwise Gemini
                    if self.model_service and self.model_service.is_available():
                        response_text = await self.model_service.generate(prompt)
                        # Create a response-like object for compatibility
                        class Response:
                            def __init__(self, text):
                                self.text = text
                        response = Response(response_text)
                    elif self.model:
                        # Use Gemini (synchronous call)
                        response = self.model.generate_content(prompt)
                    else:
                        raise Exception("No model available")
                    
                    elapsed = time.time() - start_time
                    print(f"[Copilot] Model API call completed in {elapsed:.2f}s")
                    return response
                except Exception as e:
                    elapsed = time.time() - start_time
                    print(f"[Copilot] Model API call failed after {elapsed:.2f}s: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            
            # Execute in thread pool with timeout
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # If no running loop, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            api_start = time.time()
            
            try:
                # Use reasonable timeout
                # For custom models, use async directly; for Gemini, use executor
                if self.model_service and self.model_service.is_available():
                    response = await asyncio.wait_for(
                        call_model(),
                        timeout=60.0  # Custom models may take longer
                    )
                else:
                    # Gemini needs to run in executor since it's synchronous
                    def call_gemini_sync():
                        return self.model.generate_content(prompt)
                    
                    response = await asyncio.wait_for(
                        loop.run_in_executor(None, call_gemini_sync),
                        timeout=30.0  # 30 second timeout for Gemini
                    )
                api_elapsed = time.time() - api_start
                print(f"[Copilot] Total API wait time: {api_elapsed:.2f}s")
            except asyncio.TimeoutError:
                elapsed = time.time() - api_start
                print(f"[Copilot] Gemini API timeout after {elapsed:.2f}s")
                return {
                    "answer": "Ugh, I'm taking forever! 😅 Sorry about that - I'm a bit slow today. Try:\n- Asking me something simpler\n- Checking your internet\n- Give me another shot in a sec! 💕",
                    "sources": [],
                    "data": relevant_data.get("data", {})
                }
            except Exception as e:
                elapsed = time.time() - api_start
                error_msg = str(e)
                print(f"[Copilot] Error during API call after {elapsed:.2f}s: {error_msg}")
                import traceback
                traceback.print_exc()
                
                # Check if it's a quota error - if so, return a helpful message instead of raising
                if "ResourceExhausted" in error_msg or "429" in error_msg or ("quota" in error_msg.lower() and "exceeded" in error_msg.lower()):
                    # Extract retry time if available
                    retry_seconds = None
                    if "retry in" in error_msg.lower() or "retry_delay" in error_msg.lower():
                        import re
                        match = re.search(r'retry in ([\d.]+)s', error_msg.lower())
                        if match:
                            retry_seconds = int(float(match.group(1)))
                    
                    user_error_msg = "I'm having trouble connecting to the AI service right now. "
                    if retry_seconds:
                        user_error_msg += f"The AI service quota has been exceeded. Please try again in {retry_seconds} seconds."
                    else:
                        user_error_msg += "The AI service quota has been exceeded. Please try again in a minute."
                    
                    return {
                        "answer": user_error_msg,
                        "sources": relevant_data.get("sources", []) if isinstance(relevant_data.get("sources"), list) else [],
                        "data": relevant_data.get("data", {}) if isinstance(relevant_data.get("data"), dict) else {}
                    }
                
                # For other errors, raise to be handled by outer exception handler
                raise
            
            # Extract answer from response
            answer = "Oops! 😅 I'm having a little trouble right now. Can you try asking me again?"
            if response:
                if hasattr(response, 'text'):
                    answer = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    # Handle different response formats
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content'):
                        if hasattr(candidate.content, 'parts'):
                            answer = candidate.content.parts[0].text if candidate.content.parts else answer
                        elif hasattr(candidate.content, 'text'):
                            answer = candidate.content.text
            
            if not answer or len(answer.strip()) == 0:
                answer = "Hmm, I'm drawing a blank right now! 😊 Try asking me again, maybe rephrase it?"
            
            # Ensure we always return a dict with the expected structure
            result = {
                "answer": str(answer).strip(),
                "sources": relevant_data.get("sources", []) if isinstance(relevant_data.get("sources"), list) else [],
                "data": relevant_data.get("data", {}) if isinstance(relevant_data.get("data"), dict) else {}
            }
            
            print(f"[Copilot] Returning response with answer length: {len(result['answer'])}")
            return result
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = str(e)
            print(f"[Copilot] Error in process_query: {error_msg}")
            print(f"[Copilot] Traceback:\n{error_trace}")
            
            # Build user-friendly error message
            user_error_msg = "I'm having trouble connecting to the AI service right now. "
            if "ResourceExhausted" in error_msg or "429" in error_msg or ("quota" in error_msg.lower() and "exceeded" in error_msg.lower()):
                # Extract retry time if available
                retry_seconds = None
                if "retry in" in error_msg.lower() or "retry_delay" in error_msg.lower():
                    import re
                    match = re.search(r'retry in ([\d.]+)s', error_msg.lower())
                    if match:
                        retry_seconds = int(float(match.group(1)))
                
                if retry_seconds:
                    user_error_msg += f"The AI service quota has been exceeded. Please try again in {retry_seconds} seconds."
                else:
                    user_error_msg += "The AI service quota has been exceeded. Please try again in a minute."
            elif "API key" in error_msg.lower() or "authentication" in error_msg.lower():
                user_error_msg += "There's an authentication issue with the AI service."
            elif "timeout" in error_msg.lower():
                user_error_msg += "The request timed out. Please try again."
            else:
                user_error_msg += "Please try again in a moment."
            
            # Return error response (don't raise - let endpoint handle it)
            return {
                "answer": user_error_msg,
                "sources": relevant_data.get("sources", []) if isinstance(relevant_data.get("sources"), list) else [],
                "data": relevant_data.get("data", {}) if isinstance(relevant_data.get("data"), dict) else {}
            }
    
    def _gather_context(self, query: str, context: dict) -> dict:
        """Gather relevant context from database based on query and filters"""
        sources = []
        data = {}
        filters = context.get("filters", {})
        
        # Search contracts if query mentions contracts or filters are set
        contract_filters = filters.get("contracts", {})
        if any(word in query.lower() for word in ["contract", "agreement", "supplier", "vendor"]) or contract_filters:
            query_obj = self.db.query(Contract)
            
            # Apply filters
            if contract_filters.get("status"):
                query_obj = query_obj.filter(Contract.status == contract_filters["status"])
            if contract_filters.get("contract_type"):
                query_obj = query_obj.filter(Contract.type == contract_filters["contract_type"])
            if contract_filters.get("min_risk_score") is not None:
                query_obj = query_obj.filter(Contract.risk_score >= contract_filters["min_risk_score"])
            if contract_filters.get("max_risk_score") is not None:
                query_obj = query_obj.filter(Contract.risk_score <= contract_filters["max_risk_score"])
            if contract_filters.get("min_contract_value") is not None:
                query_obj = query_obj.filter(Contract.contract_value >= contract_filters["min_contract_value"])
            if contract_filters.get("max_contract_value") is not None:
                query_obj = query_obj.filter(Contract.contract_value <= contract_filters["max_contract_value"])
            
            contracts = query_obj.limit(10).all()  # Reduced limit for faster queries
            data["contracts"] = [
                {
                    "id": c.id, 
                    "title": c.title, 
                    "status": c.status,
                    "type": c.type,
                    "risk_score": c.risk_score,
                    "contract_value": c.contract_value,
                    "party_a": c.party_a,
                    "party_b": c.party_b
                } for c in contracts
            ]
            sources.extend([f"Contract: {c.title}" for c in contracts[:3]])  # Reduced sources
        
        # Search compliance records
        compliance_filters = filters.get("compliance", {})
        if any(word in query.lower() for word in ["compliance", "gdpr", "iso", "regulation", "framework"]) or compliance_filters:
            query_obj = self.db.query(ComplianceRecord)
            
            # Apply filters
            if compliance_filters.get("framework_id"):
                query_obj = query_obj.filter(ComplianceRecord.framework_id == compliance_filters["framework_id"])
            if compliance_filters.get("status"):
                query_obj = query_obj.filter(ComplianceRecord.status == compliance_filters["status"])
            
            records = query_obj.limit(10).all()  # Reduced limit for faster queries
            data["compliance"] = [
                {
                    "id": r.id, 
                    "status": r.status, 
                    "framework_id": r.framework_id,
                    "last_assessment_date": str(r.last_assessment_date) if r.last_assessment_date else None
                } for r in records
            ]
            sources.extend([f"Compliance Record: {r.id}" for r in records[:3]])  # Reduced sources
        
        # Search reports
        report_filters = filters.get("reports", {})
        if any(word in query.lower() for word in ["report", "kpi", "metric", "dashboard"]) or report_filters:
            query_obj = self.db.query(Report)
            
            # Apply filters
            if report_filters.get("report_type"):
                query_obj = query_obj.filter(Report.report_type == report_filters["report_type"])
            
            reports = query_obj.limit(10).all()  # Reduced limit for faster queries
            data["reports"] = [
                {
                    "id": r.id, 
                    "title": r.title, 
                    "type": r.report_type,
                    "created_at": str(r.created_at) if r.created_at else None
                } for r in reports
            ]
            sources.extend([f"Report: {r.title}" for r in reports[:3]])  # Reduced sources
        
        # Dashboard data
        dashboard_filters = filters.get("dashboard", {})
        if any(word in query.lower() for word in ["dashboard", "summary", "overview", "statistics"]) or dashboard_filters:
            # Get dashboard summary data
            total_contracts = self.db.query(Contract).count()
            active_contracts = self.db.query(Contract).filter(Contract.status == "active").count()
            total_compliance = self.db.query(ComplianceRecord).count()
            compliant = self.db.query(ComplianceRecord).filter(ComplianceRecord.status == "compliant").count()
            total_reports = self.db.query(Report).count()
            
            data["dashboard"] = {
                "total_contracts": total_contracts,
                "active_contracts": active_contracts,
                "total_compliance_records": total_compliance,
                "compliant_records": compliant,
                "compliance_rate": (compliant / total_compliance * 100) if total_compliance > 0 else 0,
                "total_reports": total_reports
            }
            sources.append("Dashboard Summary")
        
        return {
            "data": data,
            "sources": sources
        }
    
    def _format_context(self, context_data: dict) -> str:
        """Format context data for AI prompt"""
        formatted = []
        
        if "contracts" in context_data.get("data", {}):
            formatted.append("Contracts:")
            for contract in context_data["data"]["contracts"][:5]:
                formatted.append(f"  - {contract['title']} (Status: {contract['status']})")
        
        if "compliance" in context_data.get("data", {}):
            formatted.append("Compliance Records:")
            for record in context_data["data"]["compliance"][:5]:
                formatted.append(f"  - Record {record['id']} (Status: {record['status']})")
        
        if "reports" in context_data.get("data", {}):
            formatted.append("Reports:")
            for report in context_data["data"]["reports"][:5]:
                formatted.append(f"  - {report['title']} (Type: {report['type']})")
        
        return "\n".join(formatted) if formatted else "No relevant context found."

