"""
Report Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class KPIResponse(BaseModel):
    id: int
    name: str
    value: str
    unit: Optional[str] = None
    trend: Optional[str] = None
    target: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    status: str
    summary: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    kpis: List[KPIResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    title: str
    report_type: str
    template_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


