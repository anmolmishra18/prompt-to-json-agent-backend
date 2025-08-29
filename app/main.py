from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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

# Create tables (with error handling for deployment)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(title=settings.APP_NAME)

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
    try:
        spec = generator.run(payload.prompt)
        report = crud.create_report(db, prompt_text=payload.prompt, json_spec=spec)
        return {"id": report.id, "json_spec": spec}
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
    try:
        spec = generator.run(payload.prompt)
        report = crud.create_report(db, prompt_text=payload.prompt, json_spec=spec)

        history = rl.run(payload.prompt, max_iters=payload.max_iters)
        for rec in history:
            crud.add_iteration(db, report.id, rec)
            if rec.get("feedback"):
                crud.add_feedback(db, report.id, rec["feedback"])

        return {
            "report_id": report.id,
            "iterations": [IterationRecord(**rec) for rec in history]
        }
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
    try:
        v = crud.log_hidg(db, payload.honesty, payload.integrity, payload.discipline, payload.gratitude)
        return {"id": v.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log values: {str(e)}")
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/hidg-logs")
def get_hidg_logs(db: Session = Depends(get_db)) -> List[dict]:
    logs = db.query(models.HIDGValue).order_by(models.HIDGValue.created_at.desc()).limit(30).all()
    return [{"id": str(log.id), "honesty": log.honesty, "integrity": log.integrity, 
             "discipline": log.discipline, "gratitude": log.gratitude, 
             "created_at": log.created_at.isoformat()} for log in logs]