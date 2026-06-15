import random
from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
import models

def seed_data(num_records=100):
    db = SessionLocal()
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("🌱 가상 데이터를 생성 중입니다...")
    
    sample_subjects = [
        {"name": "수학I", "category": 1, "credit_hours": 4},
        {"name": "국어", "category": 1, "credit_hours": 4},
        {"name": "물리학I", "category": 2, "credit_hours": 3},
        {"name": "사회·문화", "category": 2, "credit_hours": 3},
        {"name": "체육", "category": 3, "credit_hours": 1},
    ]
    
    db_subjects = []
    for s in sample_subjects:
        subject = models.Subject(**s)
        db.add(subject)
        db_subjects.append(subject)
    db.commit()

    for _ in range(num_records):
        chosen_subject = random.choice(db_subjects)
        weight = random.choice([10, 15, 20, 30, 40])
        overlapping = random.randint(0, 5)
        
        due_date = datetime.now() + timedelta(days=random.randint(-30, 30))
        
        stress = 1.5 + (weight / 20.0) + (overlapping * 0.5) + random.uniform(-0.5, 0.5)
        stress = max(1.0, min(5.0, stress))
        
        assessment = models.PerformanceAssessment(
            subject_id=chosen_subject.id,
            evaluation_type=random.randint(1, 4),
            weight=weight,
            due_date=due_date,
            overlapping_tasks=overlapping,
            actual_time_spent=round(random.uniform(1.0, 10.0), 1),
            user_stress_score=round(stress, 1)
        )
        db.add(assessment)
        
    db.commit()
    db.close()
    print(f"✅ {num_records}개의 데이터가 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    seed_data()
