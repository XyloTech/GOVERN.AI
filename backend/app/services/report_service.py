"""
Report Generation Service
"""
from sqlalchemy.orm import Session
from app.models.report import Report, KPI
from app.schemas.report import ReportCreate
from app.services.ai_service import AIService
from datetime import datetime

class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    async def generate_report(self, report_data: ReportCreate) -> Report:
        """Generate an AI-powered report"""
        # Collect data based on report type
        data = self._collect_report_data(report_data.report_type, report_data.period_start, report_data.period_end)
        
        # Generate AI summary (await the async function)
        summary = await self.ai_service.generate_report_summary(data, report_data.report_type)
        
        # Create report
        report = Report(
            title=report_data.title,
            report_type=report_data.report_type,
            status="generated",
            summary=summary,
            data=data,
            period_start=report_data.period_start,
            period_end=report_data.period_end,
            template_id=report_data.template_id
        )
        
        self.db.add(report)
        self.db.flush()
        
        # Add sample KPIs
        kpis = self._generate_kpis(report_data.report_type, data)
        for kpi_data in kpis:
            kpi = KPI(
                report_id=report.id,
                **kpi_data
            )
            self.db.add(kpi)
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def _collect_report_data(self, report_type: str, period_start: datetime = None, period_end: datetime = None) -> dict:
        """Collect data for report generation"""
        # This would integrate with ERP/CRM systems in production
        # For MVP, return sample structure
        return {
            "period": {
                "start": period_start.isoformat() if period_start else None,
                "end": period_end.isoformat() if period_end else None
            },
            "metrics": {},
            "insights": []
        }
    
    def _generate_kpis(self, report_type: str, data: dict) -> list:
        """Generate KPIs for the report"""
        # Sample KPIs based on report type
        if report_type == "financial":
            return [
                {"name": "Total Revenue", "value": "0", "unit": "USD", "trend": "stable"},
                {"name": "Operating Expenses", "value": "0", "unit": "USD", "trend": "stable"}
            ]
        elif report_type == "compliance":
            return [
                {"name": "Compliance Rate", "value": "0", "unit": "%", "trend": "stable"},
                {"name": "Active Alerts", "value": "0", "unit": "count", "trend": "stable"}
            ]
        else:
            return []

