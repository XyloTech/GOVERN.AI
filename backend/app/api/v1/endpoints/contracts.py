"""
Contract Intelligence API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.contract import Contract, ContractClause, ContractRisk
from app.schemas.contract import ContractCreate, ContractResponse, ContractClauseResponse
from app.services.contract_service import ContractService
import json

router = APIRouter()


@router.post("/upload", response_model=ContractResponse)
async def upload_contract(
    file: UploadFile = File(...),
    status: Optional[str] = Form(None),
    contract_type: Optional[str] = Form(None),
    min_risk_score: Optional[float] = Form(None),
    max_risk_score: Optional[float] = Form(None),
    min_contract_value: Optional[float] = Form(None),
    max_contract_value: Optional[float] = Form(None),
    currency: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and analyze a contract document with optional metadata/filters"""
    try:
        contract_service = ContractService(db)
        
        # Parse tags if provided
        tags_list = []
        if tags:
            try:
                tags_list = json.loads(tags) if isinstance(tags, str) else tags
            except:
                tags_list = [tags] if tags else []
        
        # Prepare metadata
        metadata = {
            'status': status,
            'contract_type': contract_type,
            'min_risk_score': min_risk_score,
            'max_risk_score': max_risk_score,
            'min_contract_value': min_contract_value,
            'max_contract_value': max_contract_value,
            'currency': currency,
            'tags': tags_list
        }
        
        contract = await contract_service.process_contract_upload(file, metadata)
        return contract
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing contract: {str(e)}"
        )


@router.get("/", response_model=List[ContractResponse])
def get_contracts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    contract_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all contracts with optional filters"""
    try:
        query = db.query(Contract)
        
        if status:
            query = query.filter(Contract.status == status)
        if contract_type:
            query = query.filter(Contract.type == contract_type)
        
        contracts = query.offset(skip).limit(limit).all()
        return contracts
    except LookupError as e:
        # Handle invalid enum values in database
        # This can happen if old data exists with invalid enum values
        # Run the fix script: python scripts/fix_contract_types.py
        raise HTTPException(
            status_code=500,
            detail=f"Database contains invalid contract types. Please run: python scripts/fix_contract_types.py. Error: {str(e)}"
        )


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """Get a specific contract by ID"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/{contract_id}/clauses", response_model=List[ContractClauseResponse])
def get_contract_clauses(contract_id: int, db: Session = Depends(get_db)):
    """Get all clauses for a contract"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract.clauses


@router.get("/{contract_id}/risks")
def get_contract_risks(contract_id: int, db: Session = Depends(get_db)):
    """Get risk analysis for a contract"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract.risks


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    """Delete a contract"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    db.delete(contract)
    db.commit()
    return {"message": "Contract deleted successfully"}

