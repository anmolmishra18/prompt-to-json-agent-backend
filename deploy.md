# Deployment Guide

## Render Deployment (Recommended)

1. **Create Render Account**: https://render.com
2. **Connect Repository**: Link your GitHub repo
3. **Create Web Service**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`
4. **Environment Variables**:
   ```
   DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
   DEBUG=false
   APP_NAME=Prompt→JSON Agent Backend
   ```

## Supabase Database Setup

1. **Create Project**: https://supabase.com
2. **Get Connection String**: Settings → Database → Connection string
3. **Update Environment**: Set DATABASE_URL in Render dashboard

## Post-Deployment Checklist

- [ ] Health check: `GET /health` returns 200
- [ ] API docs accessible: `/docs`
- [ ] Database connected: Create a report via `/generate`
- [ ] All endpoints working: Run test suite
- [ ] CORS configured for frontend domain

## Team Integration

### For Rishabh (Frontend)
- Base URL: `https://your-app.render.com`
- Endpoints: `/generate`, `/evaluate`, `/iterate`, `/reports/{id}`, `/log-values`
- Docs: `https://your-app.render.com/docs`

### For Nisarg (BHIV Core)
- All agents expose `run(input) -> output` interface
- Import: `from app.services.prompt_agent import PromptAgent`
- Usage: `agent = PromptAgent(); result = agent.run(input_data)`

### For Nipun (BHIV Bucket)
- Database models in `app/models.py`
- CRUD operations in `app/crud.py`
- HIDG logs: `GET /hidg-logs`, `POST /log-values`