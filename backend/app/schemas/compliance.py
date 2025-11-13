"""
Compliance Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ComplianceFrameworkResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ComplianceRecordResponse(BaseModel):
    id: int
    framework_id: int
    status: str
    requirement_id: Optional[str] = None
    requirement_description: Optional[str] = None
    compliance_score: Optional[int] = None
    last_assessed: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    related_contract_id: Optional[int] = None
    
    class Config:
        from_attributes = True


