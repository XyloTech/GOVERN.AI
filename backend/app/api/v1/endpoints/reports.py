"""
AI Reporting Engine API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import os
from app.core.database import get_db
from app.models.report import Report, ReportTemplate, KPI
from app.schemas.report import ReportResponse, ReportCreate
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    """Generate a new AI-powered report"""
    report_service = ReportService(db)
    report = await report_service.generate_report(report_data)
    return report


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    skip: int = 0,
    limit: int = 100,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all reports with optional filters"""
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/templates", response_model=List[dict])
def get_report_templates(db: Session = Depends(get_db)):
    """Get all report templates"""
    templates = db.query(ReportTemplate).all()
    return [{"id": t.id, "name": t.name, "description": t.description, "report_type": t.report_type} for t in templates]


@router.get("/dashboard/kpis")
def get_kpi_dashboard(
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get KPI dashboard data"""
    # This would typically aggregate KPIs from multiple reports
    # For MVP, return sample structure
    return {
        "financial_kpis": [],
        "operational_kpis": [],
        "compliance_kpis": [],
        "contract_kpis": []
    }


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Download a report in specified format (json, pdf, excel)"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if format == "json":
        # Return JSON response
        report_data = {
            "id": report.id,
            "title": report.title,
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
            "status": report.status.value if hasattr(report.status, 'value') else str(report.status),
            "summary": report.summary,
            "data": report.data,
            "visualizations": report.visualizations,
            "period_start": report.period_start.isoformat() if report.period_start else None,
            "period_end": report.period_end.isoformat() if report.period_end else None,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "kpis": [{"name": k.name, "value": k.value, "unit": k.unit, "trend": k.trend, "status": k.status} for k in report.kpis]
        }
        return JSONResponse(
            content=report_data,
            headers={
                "Content-Disposition": f'attachment; filename="{report.title.replace(" ", "_")}.json"'
            }
        )
    elif format == "pdf" and report.file_path and os.path.exists(report.file_path):
        # Return PDF file if it exists
        return FileResponse(
            report.file_path,
            media_type="application/pdf",
            filename=f"{report.title.replace(' ', '_')}.pdf"
        )
    else:
        # For PDF/Excel, if file doesn't exist, return JSON as fallback
        # In production, you would generate the PDF/Excel here
        report_data = {
            "id": report.id,
            "title": report.title,
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
            "status": report.status.value if hasattr(report.status, 'value') else str(report.status),
            "summary": report.summary,
            "data": report.data,
            "visualizations": report.visualizations,
            "period_start": report.period_start.isoformat() if report.period_start else None,
            "period_end": report.period_end.isoformat() if report.period_end else None,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "kpis": [{"name": k.name, "value": k.value, "unit": k.unit, "trend": k.trend, "status": k.status} for k in report.kpis]
        }
        return JSONResponse(
            content=report_data,
            headers={
                "Content-Disposition": f'attachment; filename="{report.title.replace(" ", "_")}.json"'
            }
        )

