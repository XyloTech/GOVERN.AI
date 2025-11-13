# Testing Contract Upload Feature

## Sample Contract Document

A sample contract document has been created at:
`backend/sample_contracts/sample_contract.txt`

This document contains:
- Contract parties (TechCorp Solutions Inc. and DataServices LLC)
- Contract value: $500,000 USD
- Dates: January 1, 2024 - December 31, 2024
- Risk factors and compliance requirements
- Terms and conditions

## How to Test

### Option 1: Via Web UI (Recommended)

1. **Open the application**: http://localhost:3000
2. **Navigate to Contracts**: Click "CONTRACTS" in the sidebar
3. **Upload the sample contract**:
   - Click "Select Document"
   - Navigate to `backend/sample_contracts/sample_contract.txt`
   - Click "UPLOAD & ANALYZE"
4. **View Results**: The AI will analyze the contract and display:
   - Extracted contract details (title, parties, dates, value)
   - Risk score
   - Risk factors
   - Tags
   - Status

### Option 2: Via API (Using PowerShell)

```powershell
$filePath = "C:\Users\HITESH_CHOUDHARY\OneDrive\Desktop\AI\backend\sample_contracts\sample_contract.txt"
$uri = "http://localhost:8000/api/v1/contracts/upload"

$form = @{
    file = Get-Item -Path $filePath
}

Invoke-RestMethod -Uri $uri -Method Post -Form $form -ContentType "multipart/form-data"
```

### Option 3: Via API Documentation

1. Open: http://localhost:8000/api/docs
2. Find: `POST /api/v1/contracts/upload`
3. Click "Try it out"
4. Click "Choose File" and select `backend/sample_contracts/sample_contract.txt`
5. Click "Execute"
6. View the response with extracted contract data

## Expected Results

After uploading, you should see:
- **Title**: Extracted from document
- **Contract Number**: Auto-generated or extracted
- **Parties**: TechCorp Solutions Inc. and DataServices LLC
- **Contract Value**: $500,000.00 USD
- **Dates**: Effective and expiration dates
- **Risk Score**: Calculated based on contract terms
- **Risk Factors**: List of identified risks
- **Tags**: Auto-generated tags

## What Happens Behind the Scenes

1. **Document Upload**: File is saved to `backend/uploads/`
2. **Text Extraction**: Document text is extracted (PDF, DOCX, or TXT)
3. **AI Analysis**: OpenAI GPT-4 analyzes the contract (or basic extraction if API key not set)
4. **Data Extraction**: 
   - Contract parties
   - Dates and terms
   - Financial values
   - Risk assessment
   - Clause extraction
5. **Database Storage**: Contract and extracted data saved to database
6. **Response**: Structured JSON with all extracted information

## Testing Different File Types

You can test with:
- **TXT files**: Plain text contracts
- **PDF files**: PDF documents (requires PyPDF2)
- **DOCX files**: Word documents (requires python-docx)

All are supported by the document processing service!


