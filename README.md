# Prompt → JSON Agent Backend (FastAPI)

Implements the 4‑day sprint plan: endpoints `/generate`, `/evaluate`, `/iterate`, `/reports/{id}`, and `/log-values`, with Postgres/Supabase-ready storage and a simple RL-style improvement loop.

## 0) Quickstart (Local, SQLite)

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install pydantic-settings   # Required dependency

# Run server (from project root)
python run.py
# OR
python -m uvicorn app.main:app --reload
```

Now open http://127.0.0.1:8000/docs

## 1) Docker (Postgres)

```bash
docker compose up --build
```

This starts Postgres + the API at http://localhost:8000

Set `DATABASE_URL` in `docker-compose.yml` for your Supabase/remote Postgres if needed.

## 2) Day-by-Day (as per task PDF)

- **Day 1**: repo structured into `app/services` with `run()` interfaces; FastAPI skeleton with `/generate` live.  
- **Day 2**: DB integration storing reports, evaluations, feedback logs, and HIDG values; `/reports/{id}`, `/log-values`.  
- **Day 3**: Feedback generation + iterative improvement loop; `/iterate` returns before→after JSONs with scores and feedback; history stored.  
- **Day 4**: Dockerize + deploy; README + docs.  

## 3) API Examples + Expected Outputs

### POST /generate
**Request**
```bash
curl -s -X POST http://localhost:8000/generate -H "Content-Type: application/json"   -d '{"prompt":"design a robot using aluminium; Priority: high"}'
```
**Expected 200 Response (example)**
```json
{
  "id": "UUID",
  "json_spec": {
    "title": "design a robot using aluminium",
    "description": "design a robot using aluminium",
    "priority": "high"
  }
}
```

### POST /evaluate
**Request (by spec)**
```bash
curl -s -X POST http://localhost:8000/evaluate -H "Content-Type: application/json"   -d '{"json_spec": {"title": "Robot", "description": "Build a robot frame using aluminium.", "priority": "high"}}'
```
**Expected 200 Response (example)**
```json
{ "score": 1.0, "comments": "Spec looks good." }
```

### POST /iterate
**Request**
```bash
curl -s -X POST http://localhost:8000/iterate -H "Content-Type: application/json"   -d '{"prompt":"design a robot using aluminium", "max_iters":2}'
```
**Expected 200 Response (example)**
```json
{
  "report_id": "UUID",
  "iterations": [
    {
      "iteration_number": 1,
      "before_json": {"title":"design a robot using aluminium","description":"design a robot using aluminium","priority":"medium"},
      "after_json":  {"title":"design a robot using aluminium","description":"design a robot using aluminium This spec includes goals, inputs, and expected outputs.","priority":"medium"},
      "score_before": 0.6,
      "score_after": 0.8,
      "feedback": "Expand the description with goals, inputs, and outputs (≥ 20 chars)."
    },
    {
      "iteration_number": 2,
      "before_json": {"title":"design a robot using aluminium","description":"design a robot using aluminium This spec includes goals, inputs, and expected outputs.","priority":"medium"},
      "after_json":  {"title":"design a robot using aluminium","description":"design a robot using aluminium This spec includes goals, inputs, and expected outputs.","priority":"medium"},
      "score_before": 0.8,
      "score_after": 0.8,
      "feedback": "Refine wording for clarity and add acceptance criteria if needed."
    }
  ]
}
```

### GET /reports/{id}
**Request**
```bash
curl -s http://localhost:8000/reports/REPLACE_WITH_ID
```
**Expected 200 Response (shape)**
```json
{
  "id": "UUID",
  "prompt_text": "…",
  "json_spec": { … },
  "evaluations": [{"id":"…","score":0.8,"comments":"…","created_at":"…"}],
  "iterations": [{"id":"…","iteration_number":1,"before_json":{…},"after_json":{…},"score_before":0.6,"score_after":0.8,"feedback":"…","created_at":"…"}],
  "feedback_logs": [{"id":"…","feedback":"…","created_at":"…"}]
}
```

### POST /log-values
**Request**
```bash
curl -s -X POST http://localhost:8000/log-values -H "Content-Type: application/json"   -d '{"honesty":"what worked/broke","integrity":"record real results","discipline":"shipped endpoints","gratitude":"thanks to team/docs"}'
```
**Expected 200 Response (example)**
```json
{ "id": "UUID" }
```

## 4) Production Deployment

### Render/Heroku
```bash
# 1. Set environment variables:
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
DEBUG=false

# 2. Deploy (Procfile included)
# Render: Connect repo, set env vars, deploy
# Heroku: git push heroku main
```

### Supabase Database
```bash
# Get connection string from Supabase dashboard:
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres?sslmode=require
```

### Production CORS
Update `app/main.py` origins for your frontend domain:
```python
origins = ["https://yourapp.com"] if not settings.DEBUG else ["*"]
```

## 5) Live Demo & Integration

**🚀 DEPLOYMENT STATUS**: ✅ LIVE AND RUNNING

### 🌐 Live Backend
- **API Base**: https://prompt-to-json-agent-backend-1.onrender.com
- **Interactive Docs**: https://prompt-to-json-agent-backend-1.onrender.com/docs
- **Health Check**: https://prompt-to-json-agent-backend-1.onrender.com/health
- **Demo UI**: Open `demo.html` in browser for quick testing

### 🎯 Enhanced Features (v1.1)
- **Comprehensive Error Handling**: Proper HTTP status codes and validation
- **HIDG Analytics**: `/hidg-analytics` endpoint with meaningful insights
- **Enhanced RL Learning**: Progressive improvement with genuine score increases
- **Input Validation**: All endpoints validate input length and format
- **Stress Testing**: Concurrent request handling verified

### Team Integration:
- **Rishabh (Frontend)**: Use `demo.html` as reference, API fully documented
- **Nisarg (BHIV Core)**: All agents ready with `run()` interface, see `bhiv_integration.md`
- **Nipun (BHIV Bucket)**: Enhanced analytics at `/hidg-analytics`, logs at `/hidg-logs`

### Daily HIDG Logging:
```bash
curl -X POST https://prompt-to-json-agent-backend-1.onrender.com/log-values \
  -H "Content-Type: application/json" \
  -d '{"honesty":"what worked/broke today","integrity":"real results recorded","discipline":"completed tasks","gratitude":"thanks to team"}'
```

### Testing:
```bash
# Run comprehensive tests
python test_api_comprehensive.py

# Quick health check
curl https://prompt-to-json-agent-backend-1.onrender.com/health
```

## 6) Notes
- Agents/classes expose a `run()` method for orchestration compatibility.
- Replace SQLite with Postgres/Supabase by setting `DATABASE_URL` in `.env` or Compose.
- This is a heuristic baseline; swap in real LLM/evaluator later.
- **Security**: `.env` removed from repo - use `.env.example` as template.
- **Error Handling**: All endpoints include comprehensive validation and error responses.
- **Analytics**: HIDG values now include meaningful insights and consistency tracking.
