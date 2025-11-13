"""
Compliance & Governance API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.compliance import ComplianceFramework, ComplianceRecord, ComplianceAlert
from app.schemas.compliance import ComplianceFrameworkResponse, ComplianceRecordResponse

router = APIRouter()


@router.get("/frameworks", response_model=List[ComplianceFrameworkResponse])
def get_frameworks(db: Session = Depends(get_db)):
    """Get all compliance frameworks"""
    frameworks = db.query(ComplianceFramework).all()
    return frameworks


@router.get("/frameworks/{framework_id}", response_model=ComplianceFrameworkResponse)
def get_framework(framework_id: int, db: Session = Depends(get_db)):
    """Get a specific compliance framework"""
    framework = db.query(ComplianceFramework).filter(ComplianceFramework.id == framework_id).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework


@router.get("/records", response_model=List[ComplianceRecordResponse])
def get_compliance_records(
    framework_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get compliance records with optional filters"""
    query = db.query(ComplianceRecord)
    
    if framework_id:
        query = query.filter(ComplianceRecord.framework_id == framework_id)
    if status:
        query = query.filter(ComplianceRecord.status == status)
    
    records = query.all()
    return records


@router.get("/records/{record_id}", response_model=ComplianceRecordResponse)
def get_compliance_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific compliance record"""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return record


@router.get("/alerts")
def get_compliance_alerts(
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get compliance alerts"""
    query = db.query(ComplianceAlert)
    
    if severity:
        query = query.filter(ComplianceAlert.severity == severity)
    if resolved is not None:
        query = query.filter(ComplianceAlert.is_resolved == resolved)
    
    alerts = query.all()
    return alerts


@router.get("/dashboard")
def get_compliance_dashboard(db: Session = Depends(get_db)):
    """Get compliance dashboard summary"""
    total_records = db.query(ComplianceRecord).count()
    compliant = db.query(ComplianceRecord).filter(ComplianceRecord.status == "compliant").count()
    non_compliant = db.query(ComplianceRecord).filter(ComplianceRecord.status == "non_compliant").count()
    at_risk = db.query(ComplianceRecord).filter(ComplianceRecord.status == "at_risk").count()
    
    active_alerts = db.query(ComplianceAlert).filter(ComplianceAlert.is_resolved == False).count()
    
    return {
        "total_records": total_records,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "at_risk": at_risk,
        "compliance_rate": (compliant / total_records * 100) if total_records > 0 else 0,
        "active_alerts": active_alerts
    }


