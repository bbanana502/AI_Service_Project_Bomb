from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    category: int
    credit_hours: int

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int
    class Config:
        from_attributes = True

class AssessmentBase(BaseModel):
    evaluation_type: int
    weight: int
    due_date: datetime
    overlapping_tasks: int = 0

class AssessmentCreate(AssessmentBase):
    subject_id: int

class AssessmentFeedback(BaseModel):
    actual_time_spent: float
    user_stress_score: float

class Assessment(AssessmentBase):
    id: int
    subject_id: int
    actual_time_spent: Optional[float] = None
    user_stress_score: Optional[float] = None
    subject: Optional[Subject] = None
    class Config:
        from_attributes = True
