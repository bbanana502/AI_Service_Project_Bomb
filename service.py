from datetime import datetime, timedelta

from sqlalchemy.orm import Session

import models
import schemas


def get_subjects(db: Session):
    return db.query(models.Subject).all()


def get_subject(db: Session, subject_id: int):
    return db.query(models.Subject).filter(models.Subject.id == subject_id).first()


def create_subject(db: Session, subject: schemas.SubjectCreate):
    db_subject = models.Subject(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_assessments(db: Session):
    return db.query(models.PerformanceAssessment).all()


def create_assessment(db: Session, assessment: schemas.AssessmentCreate):
    db_assessment = models.PerformanceAssessment(**assessment.model_dump())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


def update_feedback(db: Session, assessment_id: int, feedback: schemas.AssessmentFeedback):
    db_assessment = db.query(models.PerformanceAssessment).filter(
        models.PerformanceAssessment.id == assessment_id
    ).first()

    if db_assessment is None:
        return None

    db_assessment.actual_time_spent = feedback.actual_time_spent
    db_assessment.user_stress_score = feedback.user_stress_score
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


def get_dashboard_summary(db: Session):
    today = datetime.now()
    next_week = today + timedelta(days=7)

    tasks = db.query(models.PerformanceAssessment).filter(
        models.PerformanceAssessment.due_date.between(today, next_week)
    ).all()

    count = len(tasks)
    if count >= 4:
        status = "위험"
        message = "수행평가 폭탄 주의보입니다. 바로 계획을 세우세요."
    elif count >= 2:
        status = "경고"
        message = "마감이 가까운 수행평가가 여러 개 있습니다."
    else:
        status = "보통"
        message = "아직 수행평가 일정이 많이 몰리지는 않았습니다."

    return {
        "마감임박_수행평가_개수": count,
        "상태": status,
        "안내": message,
    }


def get_assessment_priority(db: Session):
    assessments = db.query(models.PerformanceAssessment).all()
    priority_list = []

    for assessment in assessments:
        days_left = (assessment.due_date - datetime.now()).days
        if days_left >= 0:
            priority_score = (assessment.weight * 1.5) + (30 / (days_left + 1) * 10)
            priority_list.append({
                "수행평가_id": assessment.id,
                "과목명": assessment.subject.name,
                "마감일": assessment.due_date,
                "반영비율": assessment.weight,
                "남은일수": days_left,
                "우선순위점수": round(priority_score, 2),
            })

    return sorted(priority_list, key=lambda item: item["우선순위점수"], reverse=True)


def get_user_report(db: Session):
    subjects = db.query(models.Subject).all()
    report_data = []
    all_stress_scores = []

    for subject in subjects:
        stress_scores = []
        time_spent = []
        
        for assessment in subject.assessments:
            if assessment.user_stress_score is not None:
                stress_scores.append(float(assessment.user_stress_score))
                all_stress_scores.append(float(assessment.user_stress_score))
            if assessment.actual_time_spent is not None:
                time_spent.append(float(assessment.actual_time_spent))

        if len(stress_scores) > 0:
            avg_stress = sum(stress_scores) / len(stress_scores)
            max_stress = max(stress_scores)
            min_stress = min(stress_scores)
            avg_time = sum(time_spent) / len(time_spent) if time_spent else 0.0
            
            report_data.append({
                "과목명": subject.name,
                "평균_스트레스": float(round(avg_stress, 2)),
                "최고_스트레스": float(round(max_stress, 1)),
                "최저_스트레스": float(round(min_stress, 1)),
                "평가_개수": int(len(stress_scores)),
                "평균_소요시간": float(round(avg_time, 1)),
            })

    # 스트레스가 높은 순으로 정렬
    report_data.sort(key=lambda x: x["평균_스트레스"], reverse=True)
    
    # 전체 통계
    overall_avg_stress = float(round(sum(all_stress_scores) / len(all_stress_scores), 2)) if all_stress_scores else 0.0
    
    return {
        "보고서": report_data,
        "전체_평균_스트레스": overall_avg_stress,
        "요약": "스트레스 지수가 높은 과목부터 먼저 확인하세요.",
    }
