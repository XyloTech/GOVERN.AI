"""
Contract Pydantic Schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContractClauseResponse(BaseModel):
    id: int
    clause_type: str
    clause_text: str
    extracted_data: Optional[Dict[str, Any]] = None
    page_number: Optional[int] = None
    confidence_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class ContractRiskResponse(BaseModel):
    id: int
    risk_type: str
    severity: str
    description: Optional[str] = None
    mitigation_recommendations: Optional[str] = None
    
    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: Optional[str] = None
    type: str
    status: str
    party_a: str
    party_b: str
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    contract_value: Optional[float] = None
    currency: str = "USD"
    risk_score: float = 0.0
    risk_factors: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    title: str
    contract_number: Optional[str] = None
    type: Optional[str] = None
    party_a: str
    party_b: str


