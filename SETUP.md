# GovernAI Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example and update values)
# Required: DATABASE_URL, OPENAI_API_KEY, SECRET_KEY

# Initialize database
python init_db.py

# Seed initial data (optional)
python scripts/seed_data.py

# Run server
python run.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### 3. Database Setup

#### PostgreSQL

```sql
CREATE DATABASE governai_db;
CREATE USER governai_user WITH PASSWORD 'governai_password';
GRANT ALL PRIVILEGES ON DATABASE governai_db TO governai_user;
```

Update `DATABASE_URL` in backend `.env`:
```
DATABASE_URL=postgresql://governai_user:governai_password@localhost:5432/governai_db
```

### 4. Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/governai_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000
MAX_UPLOAD_SIZE=104857600
UPLOAD_DIR=./uploads
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing the Setup

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **API Documentation**
   - Open http://localhost:8000/api/docs in browser

3. **Frontend**
   - Open http://localhost:3000 in browser

## Common Issues

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database and user exist

### OpenAI API Error
- Set OPENAI_API_KEY in .env
- For testing without OpenAI, the system will use basic extraction

### Port Already in Use
- Backend: Change port in `run.py`
- Frontend: `npm run dev -- -p 3001`

## Next Steps

1. Upload a test contract via API or frontend
2. Check compliance dashboard
3. Generate a test report
4. Try the AI Copilot


