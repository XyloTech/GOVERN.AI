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

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR
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

