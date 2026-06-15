from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import service
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="수행평가 폭탄주의보",
    description="마감이 몰린 수행평가를 확인하고 우선순위를 정리하는 수행평가 관리 프로그램"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/subjects", response_model=List[schemas.Subject], tags=["기본 관리"])
def read_subjects(db: Session = Depends(get_db)):
    return service.get_subjects(db)

@app.post("/subjects", response_model=schemas.Subject, tags=["기본 관리"])
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    return service.create_subject(db, subject)

@app.get("/assessments", response_model=List[schemas.Assessment], tags=["기본 관리"])
def read_assessments(db: Session = Depends(get_db)):
    return service.get_assessments(db)

@app.post("/assessments", response_model=schemas.Assessment, tags=["기본 관리"])
def create_assessment(assessment: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    db_subject = service.get_subject(db, assessment.subject_id)
    if db_subject is None:
        raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
    return service.create_assessment(db, assessment)

@app.post("/assessments/{assessment_id}/feedback", response_model=schemas.Assessment, tags=["기본 관리"])
def update_assessment_feedback(
    assessment_id: int,
    feedback: schemas.AssessmentFeedback,
    db: Session = Depends(get_db)
):
    db_assessment = service.update_feedback(db, assessment_id, feedback)
    if db_assessment is None:
        raise HTTPException(status_code=404, detail="수행평가를 찾을 수 없습니다.")
    return db_assessment

@app.get("/dashboard/summary", tags=["핵심 기능"])
def get_dashboard_summary(db: Session = Depends(get_db)):
    return service.get_dashboard_summary(db)

@app.get("/assessments/priority", tags=["핵심 기능"])
def get_assessment_priority(db: Session = Depends(get_db)):
    return service.get_assessment_priority(db)

@app.get("/analytics/user-report", tags=["핵심 기능"])
def get_user_report(db: Session = Depends(get_db)):
    return service.get_user_report(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
