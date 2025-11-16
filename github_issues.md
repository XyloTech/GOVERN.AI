# GitHub Issues to Create

## Issue 1: Database Schema Migration Required
**Title:** Database schema out of sync - Missing firebase_uid and photo_url columns

**Labels:** bug, database, high-priority

**Description:**
```
## Problem
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
```
```

---

## Issue 2: Gemini API Quota Exceeded
**Title:** Handle API quota errors gracefully with retry logic

**Labels:** enhancement, api, medium-priority

**Description:**
```
## Problem
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
- [ ] Cache responses to reduce API calls
```

---

## Issue 3: Frontend Connection Errors
**Title:** Improve frontend error handling and connection reliability

**Labels:** bug, frontend, medium-priority

**Description:**
```
## Problem
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
- [ ] Better error recovery mechanisms
```

---

## Issue 4: Chat History Not Persisting
**Title:** Chat history not saving or loading correctly

**Labels:** bug, feature, high-priority

**Description:**
```
## Problem
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
- Per-user chat isolation
```

---

## Issue 5: Profile Picture Not Loading
**Title:** User profile picture fails to load

**Labels:** bug, ui, low-priority

**Description:**
```
## Problem
User profile pictures from Firebase were not loading consistently.

## Solution
✅ Added error handling for image loading
✅ Fallback to avatar with user initials
✅ Reset error state when photo URL changes
✅ Better image loading states

## Status
✅ Fixed in commit 620c0a0
```

---

## Issue 6: AI Response Timeout
**Title:** AI responses taking too long or timing out

**Labels:** performance, enhancement, medium-priority

**Description:**
```
## Problem
AI responses were timing out after 30 seconds, causing poor user experience.

## Solution
✅ Increased timeout to 35 seconds
✅ Switched to faster models (gemini-2.0-flash-exp, gemini-1.5-flash)
✅ Optimized prompts for faster responses
✅ Better timeout error messages

## Status
✅ Fixed in commit 620c0a0

## Future Improvements
- [ ] Implement streaming responses
- [ ] Add progress indicators
- [ ] Cache common queries
- [ ] Optimize prompt length
```

---

## Issue 7: Contract Data Extraction Incomplete
**Title:** Contract details showing "Unknown" or "Not specified"

**Labels:** bug, feature, high-priority

**Description:**
```
## Problem
After uploading contracts, many fields showed "Unknown" or "Not specified" even when data was present in the file.

## Solution
✅ Improved regex patterns for party extraction
✅ Enhanced date parsing with multiple format support
✅ Better contract value extraction
✅ Merged AI and regex extraction results
✅ Improved AI prompt for better extraction

## Status
✅ Fixed in commit 620c0a0

## Future Improvements
- [ ] Add ML-based extraction models
- [ ] Support more document formats
- [ ] Better handling of multi-page contracts
- [ ] Validation and confidence scores
```

---

## Issue 8: Add Database Migration System
**Title:** Implement Alembic migrations for database schema changes

**Labels:** enhancement, database, medium-priority

**Description:**
```
## Problem
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
Medium - Important for production deployments
```

---

## Issue 9: Improve Error Logging
**Title:** Add structured logging and error tracking

**Labels:** enhancement, devops, low-priority

**Description:**
```
## Current State
- Basic print statements for logging
- No structured logging
- No error tracking service integration

## Proposed Improvements
- [ ] Implement structured logging (JSON format)
- [ ] Add log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Integrate with error tracking service (Sentry, etc.)
- [ ] Add request ID tracking
- [ ] Log performance metrics
- [ ] Add log rotation

## Priority
Low - Nice to have for production monitoring
```

---

## Issue 10: API Rate Limiting
**Title:** Implement rate limiting for API endpoints

**Labels:** enhancement, security, medium-priority

**Description:**
```
## Problem
No rate limiting on API endpoints, which could lead to abuse.

## Proposed Solution
- [ ] Add rate limiting middleware
- [ ] Different limits for authenticated vs unauthenticated users
- [ ] Per-endpoint rate limits
- [ ] Rate limit headers in responses
- [ ] Configurable rate limits

## Priority
Medium - Important for production security
```

