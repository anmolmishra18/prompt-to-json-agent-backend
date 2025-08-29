import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import JSON
from .database import Base

def gen_uuid():
    return str(uuid.uuid4())

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    prompt_text: Mapped[str] = mapped_column(String, nullable=False)
    json_spec = Column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="report", cascade="all, delete-orphan")
    iterations = relationship("Iteration", back_populates="report", cascade="all, delete-orphan")
    feedback_logs = relationship("FeedbackLog", back_populates="report", cascade="all, delete-orphan")

class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    report_id: Mapped[str] = mapped_column(String, ForeignKey("reports.id"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    comments: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="evaluations")

class FeedbackLog(Base):
    __tablename__ = "feedback_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    report_id: Mapped[str] = mapped_column(String, ForeignKey("reports.id"), nullable=False, index=True)
    feedback: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="feedback_logs")

class Iteration(Base):
    __tablename__ = "iterations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    report_id: Mapped[str] = mapped_column(String, ForeignKey("reports.id"), nullable=False, index=True)
    iteration_number: Mapped[int] = mapped_column(Integer, nullable=False)
    before_json = Column(JSON, nullable=False)
    after_json = Column(JSON, nullable=False)
    score_before: Mapped[float] = mapped_column(Float, nullable=False)
    score_after: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="iterations")

class HIDGValue(Base):
    __tablename__ = "hidg_values"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    honesty: Mapped[str] = mapped_column(String, nullable=False)
    integrity: Mapped[str] = mapped_column(String, nullable=False)
    discipline: Mapped[str] = mapped_column(String, nullable=False)
    gratitude: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
