# PowerShell script to initialize git and push to GitHub
# Developed by Xylotech

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GOVERN.AI - GitHub Push Script" -ForegroundColor Cyan
Write-Host "Developed by Xylotech" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Get current directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Yellow
Write-Host ""

# Check if .git exists
if (Test-Path ".git") {
    Write-Host "Git repository already initialized." -ForegroundColor Green
} else {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to initialize git repository." -ForegroundColor Red
        exit 1
    }
    Write-Host "Git repository initialized successfully." -ForegroundColor Green
}

# Check for remote
$remoteUrl = git remote get-url origin 2>$null
if ($remoteUrl) {
    Write-Host "Remote repository found: $remoteUrl" -ForegroundColor Green
} else {
    Write-Host "No remote repository configured." -ForegroundColor Yellow
    Write-Host "Please enter your GitHub repository URL (e.g., https://github.com/XyloTech/GOVERN.AI.git):" -ForegroundColor Cyan
    $repoUrl = Read-Host
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "Remote repository added: $repoUrl" -ForegroundColor Green
    } else {
        Write-Host "Warning: No remote URL provided. Skipping remote setup." -ForegroundColor Yellow
    }
}

# Add all files
Write-Host ""
Write-Host "Adding all files to git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to add files." -ForegroundColor Red
    exit 1
}
Write-Host "Files added successfully." -ForegroundColor Green

# Check if there are changes to commit
$status = git status --porcelain
if (-not $status) {
    Write-Host "No changes to commit." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Committing changes..." -ForegroundColor Yellow
    
    $commitMessage = @"
feat: Complete GOVERN.AI platform with modern UI and custom AI models

- Modern chat UI with glassmorphism effects and smooth animations
- Custom AI model support (Ollama, HuggingFace) with Gemini fallback
- Enhanced message actions: copy, speech, search, download, share, print
- Improved typography, spacing, and responsive design
- Xylotech branding and attribution throughout
- Comprehensive documentation and setup guides

Developed by Xylotech
"@
    
    git commit -m $commitMessage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to commit changes." -ForegroundColor Red
        exit 1
    }
    Write-Host "Changes committed successfully." -ForegroundColor Green
}

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow

# Check which branch we're on
$branch = git branch --show-current
if (-not $branch) {
    $branch = "main"
    git branch -M main
    Write-Host "Created and switched to 'main' branch." -ForegroundColor Green
}

# Try to push
try {
    git push -u origin $branch
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "Branch: $branch" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host "Error: Failed to push to GitHub." -ForegroundColor Red
        Write-Host "You may need to set up authentication or create the repository on GitHub first." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan

