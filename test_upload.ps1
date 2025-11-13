# Test Contract Upload Script
# Run this script to upload the sample contract via API

$filePath = Join-Path $PSScriptRoot "backend\sample_contracts\sample_contract.txt"
$uri = "http://localhost:8000/api/v1/contracts/upload"

Write-Host "Testing Contract Upload..." -ForegroundColor Cyan
Write-Host "File: $filePath" -ForegroundColor Yellow

if (-not (Test-Path $filePath)) {
    Write-Host "Error: Sample contract file not found at $filePath" -ForegroundColor Red
    exit 1
}

try {
    $file = Get-Item -Path $filePath
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($filePath)
    $fileName = $file.Name
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: text/plain",
        "",
        [System.Text.Encoding]::UTF8.GetString($fileBytes),
        "--$boundary--"
    ) -join "`r`n"
    
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyLines)
    
    Write-Host "Uploading contract..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $bodyBytes -ContentType "multipart/form-data; boundary=$boundary"
    
    Write-Host ""
    Write-Host "Contract uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Contract Details:" -ForegroundColor Cyan
    Write-Host "  Title: $($response.title)" -ForegroundColor White
    Write-Host "  Contract Number: $($response.contract_number)" -ForegroundColor White
    Write-Host "  Party A: $($response.party_a)" -ForegroundColor White
    Write-Host "  Party B: $($response.party_b)" -ForegroundColor White
    Write-Host "  Risk Score: $($response.risk_score)" -ForegroundColor White
    Write-Host "  Status: $($response.status)" -ForegroundColor White
    
    if ($response.contract_value) {
        Write-Host "  Contract Value: $($response.contract_value) $($response.currency)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "View in UI: http://localhost:3000" -ForegroundColor Yellow
    Write-Host "View in API Docs: http://localhost:8000/api/docs" -ForegroundColor Yellow
    
} catch {
    Write-Host ""
    Write-Host "Error uploading contract:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

