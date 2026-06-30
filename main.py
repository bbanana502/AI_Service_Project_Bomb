from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

import models
import schemas
import service
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="수행평가 폭탄주의보",
    description="마감이 몰린 수행평가를 확인하고 우선순위를 정리하는 수행평가 관리 프로그램"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/subjects", response_model=List[schemas.Subject], tags=["기본 관리"])
def read_subjects(db: Session = Depends(get_db)):
    # 모든 과목의 목록을 조회하는 엔드포인트
    # 반환값은 Subject 모델의 리스트
    return service.get_subjects(db)

@app.post("/subjects", response_model=schemas.Subject, tags=["기본 관리"])
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    # 새로운 과목을 생성하는 엔드포인트
    # 요청 바디로 받은 SubjectCreate 데이터를 DB에 저장하고 생성된 객체를 반환
    return service.create_subject(db, subject)

@app.get("/assessments", response_model=List[schemas.Assessment], tags=["기본 관리"])
def read_assessments(db: Session = Depends(get_db)):
    # 모든 수행평가 항목을 조회하는 엔드포인트
    # 각 항목은 PerformanceAssessment 모델에 대응하며 관련 과목 정보가 포함될 수 있음
    return service.get_assessments(db)

@app.post("/assessments", response_model=schemas.Assessment, tags=["기본 관리"])
def create_assessment(assessment: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    # 새로운 수행평가를 생성하는 엔드포인트
    # 먼저 전달된 subject_id로 과목 존재 여부를 확인하고 없으면 404 반환
    # 존재하면 PerformanceAssessment 객체를 생성해 반환
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
    # 특정 수행평가의 피드백을 업데이트하는 엔드포인트
    # 실제 소요 시간(actual_time_spent)과 사용자의 스트레스 점수(user_stress_score)를 갱신
    # 해당 수행평가가 없으면 404 반환
    db_assessment = service.update_feedback(db, assessment_id, feedback)
    if db_assessment is None:
        raise HTTPException(status_code=404, detail="수행평가를 찾을 수 없습니다.")
    return db_assessment

@app.get("/dashboard/summary", tags=["핵심 기능"])
def get_dashboard_summary(db: Session = Depends(get_db)):
    # 향후 7일 내 마감되는 수행평가 개수를 기반으로 대시보드 요약을 생성하는 엔드포인트
    # 마감 임박 개수에 따라 상태를 '위험', '경고', '보통'으로 구분해 안내 메시지를 반환
    return service.get_dashboard_summary(db)

@app.get("/assessments/priority", tags=["핵심 기능"])
def get_assessment_priority(db: Session = Depends(get_db)):
    # 수행평가에 대해 우선순위 점수를 계산해 높은 순으로 정렬해 반환하는 엔드포인트
    # 우선순위는 반영비율과 마감까지 남은일수를 기반으로 계산됨
    return service.get_assessment_priority(db)

@app.get("/analytics/user-report", tags=["핵심 기능"])
def get_user_report(db: Session = Depends(get_db)):
    # 과목별 사용자 스트레스 평균과 평가 개수를 집계해 리포트 형태로 반환하는 엔드포인트
    # 각 과목의 연관 수행평가 중 스트레스 점수가 존재하는 항목만 집계에 포함
    return service.get_user_report(db)

# 정적 파일 제공
template_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(template_dir, "templates")), name="static")

@app.get("/")
async def root():
    """프론트엔드 페이지 제공"""
    template_path = os.path.join(template_dir, "templates", "index.html")
    return FileResponse(template_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
