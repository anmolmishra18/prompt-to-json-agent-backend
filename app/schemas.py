from typing import Optional, List, Any
from pydantic import BaseModel, Field

# ----- Agent I/O -----

class PromptIn(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, example="Title: Student Portal; Description: Manage courses, students, and grades; Priority: high")

class GenerateOut(BaseModel):
    id: str
    json_spec: dict

class EvaluateIn(BaseModel):
    report_id: Optional[str] = None
    json_spec: Optional[dict] = None

class EvaluateOut(BaseModel):
    score: float
    comments: str

class IterateIn(BaseModel):
    prompt: str
    max_iters: int = Field(default=2, ge=1, le=8)

class IterationRecord(BaseModel):
    iteration_number: int
    before_json: dict
    after_json: dict
    score_before: float
    score_after: float
    feedback: str

class IterateOut(BaseModel):
    report_id: str
    iterations: List[IterationRecord]

# ----- HIDG -----

class HIDGIn(BaseModel):
    honesty: str = Field(..., min_length=1, max_length=500)
    integrity: str = Field(..., min_length=1, max_length=500)
    discipline: str = Field(..., min_length=1, max_length=500)
    gratitude: str = Field(..., min_length=1, max_length=500)

class HIDGOut(BaseModel):
    id: str

# ----- Reports -----

class ReportOut(BaseModel):
    id: str
    prompt_text: str
    json_spec: dict
    evaluations: List[dict]
    iterations: List[dict]
    feedback_logs: List[dict]
