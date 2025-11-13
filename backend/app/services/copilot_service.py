"""
AI Copilot Service using Google Gemini
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
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use gemini-2.5-flash for fast, high-quality responses
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
    
    async def process_query(self, query: str, context: dict = None) -> dict:
        """Process natural language query using AI Copilot"""
        # Gather relevant context from database
        relevant_data = self._gather_context(query, context or {})
        
        if not self.model:
            return {
                "answer": "AI Copilot is not configured. Please set GEMINI_API_KEY in environment variables.",
                "sources": [],
                "data": relevant_data.get("data", {})
            }
        
        # Build filter description
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
        
        prompt = f"""
        You are the GovernAI Copilot, an AI assistant for enterprise governance, compliance, and contract management.
        
        User Query: {query}
        {filters_desc}
        
        Relevant Context Data:
        {self._format_context(relevant_data)}
        
        Provide a helpful, accurate answer based on the context data. Format your response clearly with:
        - A direct answer to the query
        - Key insights from the data
        - Specific numbers and statistics when available
        - Use markdown formatting for better readability (use **bold** for important points, `code` for values)
        
        If you don't have enough information, say so and suggest what additional data might be needed.
        """
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            return {
                "answer": answer,
                "sources": relevant_data.get("sources", []),
                "data": relevant_data.get("data", {})
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "data": relevant_data.get("data", {})
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
            
            contracts = query_obj.limit(20).all()
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
            sources.extend([f"Contract: {c.title}" for c in contracts[:5]])
        
        # Search compliance records
        compliance_filters = filters.get("compliance", {})
        if any(word in query.lower() for word in ["compliance", "gdpr", "iso", "regulation", "framework"]) or compliance_filters:
            query_obj = self.db.query(ComplianceRecord)
            
            # Apply filters
            if compliance_filters.get("framework_id"):
                query_obj = query_obj.filter(ComplianceRecord.framework_id == compliance_filters["framework_id"])
            if compliance_filters.get("status"):
                query_obj = query_obj.filter(ComplianceRecord.status == compliance_filters["status"])
            
            records = query_obj.limit(20).all()
            data["compliance"] = [
                {
                    "id": r.id, 
                    "status": r.status, 
                    "framework_id": r.framework_id,
                    "last_assessment_date": str(r.last_assessment_date) if r.last_assessment_date else None
                } for r in records
            ]
            sources.extend([f"Compliance Record: {r.id}" for r in records[:5]])
        
        # Search reports
        report_filters = filters.get("reports", {})
        if any(word in query.lower() for word in ["report", "kpi", "metric", "dashboard"]) or report_filters:
            query_obj = self.db.query(Report)
            
            # Apply filters
            if report_filters.get("report_type"):
                query_obj = query_obj.filter(Report.report_type == report_filters["report_type"])
            
            reports = query_obj.limit(20).all()
            data["reports"] = [
                {
                    "id": r.id, 
                    "title": r.title, 
                    "type": r.report_type,
                    "created_at": str(r.created_at) if r.created_at else None
                } for r in reports
            ]
            sources.extend([f"Report: {r.title}" for r in reports[:5]])
        
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

