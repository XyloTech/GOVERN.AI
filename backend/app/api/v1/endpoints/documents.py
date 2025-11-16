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
    # Save file and extract text
    file_content = await file.read()
    file_path = await document_service.save_uploaded_file(file, file_content)
    text_content = await document_service.extract_text_from_content(file_content, file.filename)
    return {
        "filename": file.filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "text_extracted": len(text_content) > 0,
        "text_length": len(text_content)
    }


@router.post("/batch-upload")
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple documents for batch processing"""
    document_service = DocumentService(db)
    results = []
    for file in files:
        file_content = await file.read()
        file_path = await document_service.save_uploaded_file(file, file_content)
        text_content = await document_service.extract_text_from_content(file_content, file.filename)
        results.append({
            "filename": file.filename,
            "file_path": file_path,
            "file_type": file.content_type,
            "text_extracted": len(text_content) > 0,
            "text_length": len(text_content)
        })
    return {"processed": len(results), "results": results}


@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze uploaded file and return comprehensive AI-powered analysis"""
    document_service = DocumentService(db)
    analysis = await document_service.analyze_file(file)
    return analysis



