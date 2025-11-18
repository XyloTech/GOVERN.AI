"""
Script to create GitHub issues for the GovernAI project
Requires: pip install PyGithub
Usage: python create_github_issues.py
"""
from github import Github
import os

# Get GitHub token from environment or prompt
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = "XyloTech/GOVERN.AI"

if not GITHUB_TOKEN:
    print("Please set GITHUB_TOKEN environment variable or enter it below:")
    GITHUB_TOKEN = input("GitHub Token: ").strip()

if not GITHUB_TOKEN:
    print("Error: GitHub token is required")
    exit(1)

# Initialize GitHub
try:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    # Test access
    repo.get_issues(state='open', per_page=1)
    print(f"✅ Successfully connected to repository: {REPO_NAME}")
except Exception as e:
    print(f"❌ Error connecting to repository: {e}")
    print("\n⚠️  Token permissions issue. Please ensure your token has:")
    print("   - 'repo' scope (full control of private repositories)")
    print("   - Write access to issues")
    print("\nTo fix:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Edit your token or create a new one")
    print("3. Select scope: 'repo' (includes issues)")
    print("4. Regenerate and use the new token")
    exit(1)

# Issues to create
issues = [
    {
        "title": "Database Schema Migration Required",
        "body": """## Problem
The database schema was out of sync with the User model, causing 500 errors when trying to query users with Firebase authentication.

## Error
```
sqlalchemy.exc.OperationalError: no such column: users.firebase_uid
```

## Solution
- Recreated database tables with all required columns
- Added `firebase_uid` column to users table
- Added `photo_url` column to users table
- Added `ChatMessage` table with `message_metadata` column

## Status
✅ Fixed in commit 620c0a0

## Action Required
If deploying to a new environment, run:
```python
from app.core.database import Base, engine
from app.models import User, ChatMessage, Contract, ComplianceRecord, Report
Base.metadata.create_all(bind=engine)
```""",
        "labels": ["bug", "database", "high-priority"]
    },
    {
        "title": "Handle API Quota Errors Gracefully",
        "body": """## Problem
When Gemini API quota is exceeded, users see generic error messages without knowing when to retry.

## Current Behavior
- Generic error: "I'm having trouble connecting to the AI service right now"
- No indication of retry time
- All models fail if quota is exceeded

## Solution Implemented
✅ Added quota error detection
✅ Extract and display retry time from API errors
✅ Try multiple models (gemini-1.5-flash first, then fallbacks)
✅ Better error messages with specific retry times

## Status
✅ Fixed in commit 620c0a0

## Future Improvements
- [ ] Implement automatic retry with exponential backoff
- [ ] Add quota monitoring dashboard
- [ ] Support multiple API keys with rotation
- [ ] Cache responses to reduce API calls""",
        "labels": ["enhancement", "api", "medium-priority"]
    },
    {
        "title": "Improve Frontend Error Handling",
        "body": """## Problem
Frontend was experiencing connection errors even when backend was running, due to CORS and network issues.

## Issues Fixed
✅ CORS configuration improved (allows all origins in dev)
✅ Added native fetch API fallback when axios fails
✅ Better error messages with diagnostic information
✅ Connection test on component mount
✅ Automatic token refresh on 401 errors

## Status
✅ Fixed in commit 620c0a0

## Future Improvements
- [ ] Add connection status indicator in UI
- [ ] Implement request queuing for offline scenarios
- [ ] Add retry logic with exponential backoff
- [ ] Better error recovery mechanisms""",
        "labels": ["bug", "frontend", "medium-priority"]
    },
    {
        "title": "Chat History Not Persisting",
        "body": """## Problem
Chat messages were not being saved or loaded correctly due to:
- SQLAlchemy reserved keyword conflict (`metadata` column)
- Missing user authentication context
- Incorrect response format

## Solution
✅ Renamed `metadata` column to `message_metadata`
✅ Added user authentication to all chat endpoints
✅ Fixed response format to match frontend expectations
✅ Added chat history sidebar with reload/clear functionality

## Status
✅ Fixed in commit 620c0a0

## Features Added
- Chat history sidebar
- Reload chat history button
- Clear chat history button
- Per-user chat isolation""",
        "labels": ["bug", "feature", "high-priority"]
    },
    {
        "title": "Implement Database Migration System",
        "body": """## Problem
Database schema changes require manual recreation, which is not suitable for production.

## Current State
- Using `Base.metadata.create_all()` which doesn't handle migrations
- Manual database recreation required for schema changes

## Proposed Solution
- [ ] Set up Alembic for database migrations
- [ ] Create initial migration
- [ ] Add migration for Firebase auth columns
- [ ] Document migration process
- [ ] Add migration scripts to deployment

## Priority
Medium - Important for production deployments""",
        "labels": ["enhancement", "database", "medium-priority"]
    },
    {
        "title": "Add API Rate Limiting",
        "body": """## Problem
No rate limiting on API endpoints, which could lead to abuse.

## Proposed Solution
- [ ] Add rate limiting middleware
- [ ] Different limits for authenticated vs unauthenticated users
- [ ] Per-endpoint rate limits
- [ ] Rate limit headers in responses
- [ ] Configurable rate limits

## Priority
Medium - Important for production security""",
        "labels": ["enhancement", "security", "medium-priority"]
    }
]

def create_issues():
    """Create all issues in the repository"""
    created = []
    failed = []
    
    for issue_data in issues:
        try:
            # Get or create labels
            labels = []
            for label_name in issue_data["labels"]:
                try:
                    label = repo.get_label(label_name)
                    labels.append(label)
                except:
                    # Create label if it doesn't exist
                    try:
                        label = repo.create_label(label_name, "0366d6")
                        labels.append(label)
                    except:
                        print(f"Warning: Could not create label '{label_name}'")
            
            # Create issue
            issue = repo.create_issue(
                title=issue_data["title"],
                body=issue_data["body"],
                labels=labels
            )
            created.append(issue.number)
            print(f"✅ Created issue #{issue.number}: {issue_data['title']}")
        except Exception as e:
            failed.append((issue_data["title"], str(e)))
            print(f"❌ Failed to create issue '{issue_data['title']}': {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Created: {len(created)} issues")
    print(f"   Failed: {len(failed)} issues")
    if created:
        print(f"   Issue numbers: {', '.join(map(str, created))}")

if __name__ == "__main__":
    try:
        create_issues()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Installed PyGithub: pip install PyGithub")
        print("2. Set GITHUB_TOKEN environment variable")
        print("3. Token has 'repo' scope permissions")

