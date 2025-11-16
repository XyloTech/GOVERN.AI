"""
Document Processing Service
"""
from sqlalchemy.orm import Session
from fastapi import UploadFile
import aiofiles
import os
from app.core.config import settings
from PyPDF2 import PdfReader
from docx import Document
from app.services.ai_service import AIService

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR
        self.ai_service = AIService()
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile, content: bytes) -> str:
        """Save uploaded file to disk"""
        file_path = os.path.join(self.upload_dir, file.filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_path
    
    async def extract_text_from_content(self, content: bytes, filename: str) -> str:
        """Extract text content from document bytes"""
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_extension == 'pdf':
            # Reset file pointer for PDF reader
            from io import BytesIO
            pdf_file = BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file_extension in ['docx', 'doc']:
            from io import BytesIO
            doc_file = BytesIO(content)
            doc = Document(doc_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        
        elif file_extension == 'txt':
            return content.decode('utf-8')
        
        else:
            # Try to decode as text
            try:
                return content.decode('utf-8')
            except:
                return ""
    
    async def analyze_file(self, file: UploadFile) -> dict:
        """Analyze uploaded file and return comprehensive analysis"""
        # Read file content
        file_content = await file.read()
        
        # Extract text from document
        text_content = await self.extract_text_from_content(file_content, file.filename)
        
        if not text_content or len(text_content.strip()) == 0:
            return {
                "error": "Could not extract text from file. File may be empty or in an unsupported format.",
                "filename": file.filename,
                "file_type": file.content_type
            }
        
        # Use AI to analyze the file
        analysis = await self.ai_service.analyze_file(
            text_content, 
            file.filename, 
            file.content_type
        )
        
        # Save file for reference
        file_path = await self.save_uploaded_file(file, file_content)
        analysis["file_path"] = file_path
        analysis["file_size"] = len(file_content)
        
        return analysis

