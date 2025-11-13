"""
Contract Intelligence Service
"""
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.contract import Contract, ContractClause, ContractRisk
from app.services.ai_service import AIService
from app.services.document_service import DocumentService
import uuid
from datetime import datetime
from dateutil import parser

class ContractService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.document_service = DocumentService(db)
    
    async def process_contract_upload(self, file: UploadFile, metadata: dict = None) -> Contract:
        """Process uploaded contract file and extract intelligence with optional metadata"""
        # Read file content first
        file_content = await file.read()
        
        # Save file
        file_path = await self.document_service.save_uploaded_file(file, file_content)
        
        # Extract text from document
        text_content = await self.document_service.extract_text_from_content(file_content, file.filename)
        
        # Use AI to analyze contract
        analysis = await self.ai_service.analyze_contract(text_content)
        
        # Parse dates from strings to datetime objects
        def parse_date(date_str):
            if not date_str:
                return None
            if isinstance(date_str, datetime):
                return date_str
            try:
                return parser.parse(str(date_str))
            except:
                return None
        
        # Normalize contract type to match enum - use metadata if provided, otherwise use AI analysis
        contract_type = (metadata.get("contract_type") if metadata else None) or analysis.get("type", "other")
        type_mapping = {
            "supplier": "supplier",
            "customer": "customer",
            "partnership": "partnership",
            "employment": "employment",
            "nda": "nda",
            "parties": "other",  # Fix invalid enum value
            "other": "other"
        }
        normalized_type = type_mapping.get(contract_type.lower(), "other") if contract_type else "other"
        
        # Use metadata to override AI-extracted values if provided
        status = (metadata.get("status") if metadata else None) or analysis.get("status", "draft")
        currency = (metadata.get("currency") if metadata else None) or analysis.get("currency", "USD")
        
        # Merge tags from metadata and analysis
        tags_from_metadata = metadata.get("tags", []) if metadata else []
        tags_from_analysis = analysis.get("tags", [])
        combined_tags = list(set(tags_from_metadata + tags_from_analysis))
        
        # Apply risk score filters if provided (for validation)
        risk_score = analysis.get("risk_score", 0.0)
        if metadata:
            if metadata.get("min_risk_score") is not None and risk_score < metadata.get("min_risk_score"):
                risk_score = metadata.get("min_risk_score")
            if metadata.get("max_risk_score") is not None and risk_score > metadata.get("max_risk_score"):
                risk_score = metadata.get("max_risk_score")
        
        # Apply contract value filters if provided
        contract_value = analysis.get("contract_value")
        if metadata and contract_value:
            if metadata.get("min_contract_value") is not None and contract_value < metadata.get("min_contract_value"):
                contract_value = metadata.get("min_contract_value")
            if metadata.get("max_contract_value") is not None and contract_value > metadata.get("max_contract_value"):
                contract_value = metadata.get("max_contract_value")
        
        # Create contract record
        contract = Contract(
            title=analysis.get("title", file.filename),
            contract_number=analysis.get("contract_number") or f"CNT-{uuid.uuid4().hex[:8].upper()}",
            type=normalized_type,
            status=status,
            party_a=analysis.get("party_a", "Unknown"),
            party_b=analysis.get("party_b", "Unknown"),
            effective_date=parse_date(analysis.get("effective_date")),
            expiration_date=parse_date(analysis.get("expiration_date")),
            renewal_date=parse_date(analysis.get("renewal_date")),
            contract_value=contract_value,
            currency=currency,
            file_path=file_path,
            file_name=file.filename,
            file_type=file.content_type,
            extracted_clauses=analysis.get("clauses", []),
            risk_score=risk_score,
            risk_factors=analysis.get("risk_factors", []),
            tags=combined_tags
        )
        
        self.db.add(contract)
        self.db.flush()
        
        # Create clause records
        for clause_data in analysis.get("clauses", []):
            clause = ContractClause(
                contract_id=contract.id,
                clause_type=clause_data.get("type", "general"),
                clause_text=clause_data.get("text", ""),
                extracted_data=clause_data.get("data", {}),
                confidence_score=clause_data.get("confidence", 0.0)
            )
            self.db.add(clause)
        
        # Create risk records
        for risk_data in analysis.get("risks", []):
            risk = ContractRisk(
                contract_id=contract.id,
                risk_type=risk_data.get("type", "general"),
                severity=risk_data.get("severity", "low"),
                description=risk_data.get("description"),
                mitigation_recommendations=risk_data.get("mitigation")
            )
            self.db.add(risk)
        
        self.db.commit()
        self.db.refresh(contract)
        
        return contract

