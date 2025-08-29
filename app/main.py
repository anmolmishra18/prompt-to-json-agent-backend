from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .database import Base, engine, get_db
from .config import settings
from . import models, crud
from .schemas import (
    PromptIn, GenerateOut, EvaluateIn, EvaluateOut,
    IterateIn, IterateOut, IterationRecord,
    HIDGIn, HIDGOut, ReportOut
)
from typing import List
from .services.prompt_agent import PromptAgent
from .services.evaluator import Evaluator
from .services.rl_agent import RLAgent
import logging
import traceback

# Create tables (with error handling for deployment)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(title=settings.APP_NAME)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_type": type(exc).__name__}
    )

# Validation error handler
@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": f"Validation error: {str(exc)}", "error_type": "ValidationError"}
    )

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://localhost:8080",
    "https://your-frontend-domain.com",  # Update with actual frontend URL
] if not settings.DEBUG else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

generator = PromptAgent()
evaluator = Evaluator()
rl = RLAgent()

@app.post("/generate", response_model=GenerateOut, summary="Input prompt → JSON spec")
def generate(payload: PromptIn, db: Session = Depends(get_db)):
    if not payload.prompt or not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if len(payload.prompt) > 5000:
        raise HTTPException(status_code=400, detail="Prompt too long (max 5000 chars)")
    
    try:
        spec = generator.run(payload.prompt.strip())
        if not spec or not isinstance(spec, dict):
            raise ValueError("Invalid JSON spec generated")
        report = crud.create_report(db, prompt_text=payload.prompt.strip(), json_spec=spec)
        return {"id": report.id, "json_spec": spec}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/evaluate", response_model=EvaluateOut, summary="Evaluate a JSON spec")
def evaluate(payload: EvaluateIn, db: Session = Depends(get_db)):
    try:
        if payload.report_id:
            rpt = crud.get_report(db, payload.report_id)
            if not rpt:
                raise HTTPException(status_code=404, detail="Report not found")
            spec = rpt.json_spec
        elif payload.json_spec:
            spec = payload.json_spec
        else:
            raise HTTPException(status_code=400, detail="Provide report_id or json_spec")

        res = evaluator.run(spec)
        if payload.report_id:
            crud.add_evaluation(db, payload.report_id, res["score"], res["comments"])
        return {"score": res["score"], "comments": res["comments"]}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/iterate", response_model=IterateOut, summary="Iterative improvement loop (RL-ish)")
def iterate(payload: IterateIn, db: Session = Depends(get_db)):
    if not payload.prompt or not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if payload.max_iters < 1 or payload.max_iters > 10:
        raise HTTPException(status_code=400, detail="max_iters must be between 1 and 10")
    
    try:
        spec = generator.run(payload.prompt.strip())
        if not spec or not isinstance(spec, dict):
            raise ValueError("Invalid JSON spec generated")
        report = crud.create_report(db, prompt_text=payload.prompt.strip(), json_spec=spec)

        history = rl.run(payload.prompt.strip(), max_iters=payload.max_iters)
        if not history:
            raise ValueError("No iterations generated")
            
        for rec in history:
            crud.add_iteration(db, report.id, rec)
            if rec.get("feedback"):
                crud.add_feedback(db, report.id, rec["feedback"])

        return {
            "report_id": report.id,
            "iterations": [IterationRecord(**rec) for rec in history]
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Iteration failed: {str(e)}")

@app.get("/reports/{report_id}", response_model=ReportOut, summary="Fetch a full report with history")
def get_report(report_id: str, db: Session = Depends(get_db)):
    try:
        rpt = crud.get_report(db, report_id)
        if not rpt:
            raise HTTPException(status_code=404, detail="Report not found")
        return {
            "id": rpt.id,
            "prompt_text": rpt.prompt_text,
            "json_spec": rpt.json_spec,
            "evaluations": [
                {"id": e.id, "score": e.score, "comments": e.comments, "created_at": e.created_at.isoformat()}
                for e in rpt.evaluations
            ],
            "iterations": [
                {
                    "id": it.id,
                    "iteration_number": it.iteration_number,
                    "before_json": it.before_json,
                    "after_json": it.after_json,
                    "score_before": it.score_before,
                    "score_after": it.score_after,
                    "feedback": it.feedback,
                    "created_at": it.created_at.isoformat(),
                }
                for it in rpt.iterations
            ],
            "feedback_logs": [
                {"id": f.id, "feedback": f.feedback, "created_at": f.created_at.isoformat()}
                for f in rpt.feedback_logs
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@app.post("/log-values", response_model=HIDGOut, summary="Store daily Honesty/Integrity/Discipline/Gratitude")
def log_values(payload: HIDGIn, db: Session = Depends(get_db)):
    # Validate HIDG values
    for field, value in [("honesty", payload.honesty), ("integrity", payload.integrity), 
                        ("discipline", payload.discipline), ("gratitude", payload.gratitude)]:
        if not value or not value.strip():
            raise HTTPException(status_code=400, detail=f"{field} cannot be empty")
        if len(value) > 1000:
            raise HTTPException(status_code=400, detail=f"{field} too long (max 1000 chars)")
    
    try:
        v = crud.log_hidg(db, payload.honesty.strip(), payload.integrity.strip(), 
                         payload.discipline.strip(), payload.gratitude.strip())
        return {"id": v.id}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log values: {str(e)}")
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": "1.0.0",
        "database": db_status,
        "endpoints": ["/generate", "/evaluate", "/iterate", "/reports/{id}", "/log-values", "/hidg-logs", "/hidg-analytics"]
    }

@app.get("/hidg-logs")
def get_hidg_logs(limit: int = 30, db: Session = Depends(get_db)) -> dict:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    logs = db.query(models.HIDGValue).order_by(models.HIDGValue.created_at.desc()).limit(limit).all()
    total_count = db.query(models.HIDGValue).count()
    
    return {
        "logs": [{"id": str(log.id), "honesty": log.honesty, "integrity": log.integrity, 
                 "discipline": log.discipline, "gratitude": log.gratitude, 
                 "created_at": log.created_at.isoformat()} for log in logs],
        "total_count": total_count,
        "showing": len(logs)
    }

@app.get("/hidg-analytics")
def get_hidg_analytics(db: Session = Depends(get_db)) -> dict:
    """Get analytics on HIDG values for meaningful insights"""
    logs = db.query(models.HIDGValue).order_by(models.HIDGValue.created_at.desc()).limit(100).all()
    if not logs:
        return {"message": "No HIDG logs found", "analytics": {}}
    
    # Simple analytics
    avg_lengths = {
        "honesty": sum(len(log.honesty) for log in logs) / len(logs),
        "integrity": sum(len(log.integrity) for log in logs) / len(logs),
        "discipline": sum(len(log.discipline) for log in logs) / len(logs),
        "gratitude": sum(len(log.gratitude) for log in logs) / len(logs)
    }
    
    return {
        "total_entries": len(logs),
        "latest_entry": logs[0].created_at.isoformat() if logs else None,
        "average_reflection_length": avg_lengths,
        "consistency_score": min(len(logs) / 30, 1.0),  # Based on daily logging
        "sample_recent": {
            "honesty": logs[0].honesty[:100] + "..." if len(logs[0].honesty) > 100 else logs[0].honesty,
            "gratitude": logs[0].gratitude[:100] + "..." if len(logs[0].gratitude) > 100 else logs[0].gratitude
        } if logs else {}
    }