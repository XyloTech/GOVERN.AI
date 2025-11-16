# How to Create GitHub Issues

## Option 1: Using Python Script (Recommended)

1. **Install PyGithub:**
   ```bash
   pip install PyGithub
   ```

2. **Get GitHub Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy the token

3. **Set the token and run the script:**
   ```bash
   # Windows PowerShell
   $env:GITHUB_TOKEN="your_token_here"
   python create_github_issues.py
   
   # Or enter it when prompted
   python create_github_issues.py
   ```

## Option 2: Manual Creation via GitHub Web Interface

1. Go to: https://github.com/XyloTech/GOVERN.AI/issues
2. Click "New issue"
3. Use the templates from `github_issues.md`

## Option 3: Using GitHub CLI (if installed)

```bash
# Install GitHub CLI first
# Then authenticate
gh auth login

# Create issues using the script
gh issue create --title "Title" --body "Body" --label "bug,enhancement"
```

## Issues to Create

The script will create the following issues:

1. ✅ **Database Schema Migration Required** (bug, database, high-priority)
2. ✅ **Handle API Quota Errors Gracefully** (enhancement, api, medium-priority)
3. ✅ **Improve Frontend Error Handling** (bug, frontend, medium-priority)
4. ✅ **Chat History Not Persisting** (bug, feature, high-priority)
5. ✅ **Implement Database Migration System** (enhancement, database, medium-priority)
6. ✅ **Add API Rate Limiting** (enhancement, security, medium-priority)

## Issue Details

All issue details are in `github_issues.md` file.

