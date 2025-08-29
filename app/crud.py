from typing import Union
from sqlalchemy.orm import Session
from . import models

def create_report(db: Session, prompt_text: str, json_spec: dict) -> models.Report:
    try:
        r = models.Report(prompt_text=prompt_text, json_spec=json_spec)
        db.add(r)
        db.commit()
        db.refresh(r)
        return r
    except Exception:
        db.rollback()
        raise

def get_report(db: Session, report_id: str) -> Union[models.Report, None]:
    return db.query(models.Report).filter_by(id=report_id).first()

def add_evaluation(db: Session, report_id: str, score: float, comments: str) -> models.Evaluation:
    try:
        e = models.Evaluation(report_id=report_id, score=score, comments=comments)
        db.add(e)
        db.commit()
        db.refresh(e)
        return e
    except Exception:
        db.rollback()
        raise

def add_feedback(db: Session, report_id: str, feedback: str) -> models.FeedbackLog:
    try:
        f = models.FeedbackLog(report_id=report_id, feedback=feedback)
        db.add(f)
        db.commit()
        db.refresh(f)
        return f
    except Exception:
        db.rollback()
        raise

def add_iteration(db: Session, report_id: str, rec: dict):
    try:
        it = models.Iteration(
            report_id=report_id,
            iteration_number=rec["iteration_number"],
            before_json=rec["before_json"],
            after_json=rec["after_json"],
            score_before=rec["score_before"],
            score_after=rec["score_after"],
            feedback=rec["feedback"]
        )
        db.add(it)
        db.commit()
        db.refresh(it)
        return it
    except Exception:
        db.rollback()
        raise

def log_hidg(db: Session, honesty: str, integrity: str, discipline: str, gratitude: str) -> models.HIDGValue:
    try:
        v = models.HIDGValue(honesty=honesty, integrity=integrity, discipline=discipline, gratitude=gratitude)
        db.add(v)
        db.commit()
        db.refresh(v)
        return v
    except Exception:
        db.rollback()
        raise
