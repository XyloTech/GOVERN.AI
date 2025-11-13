"""
Document Processing API Endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document for processing"""
    document_service = DocumentService(db)
    result = await document_service.process_document(file)
    return result


@router.post("/batch-upload")
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple documents for batch processing"""
    document_service = DocumentService(db)
    results = []
    for file in files:
        result = await document_service.process_document(file)
        results.append(result)
    return {"processed": len(results), "results": results}


