from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(Integer, nullable=False)
    credit_hours = Column(Integer, nullable=False)

    assessments = relationship("PerformanceAssessment", back_populates="subject", cascade="all, delete-orphan")

class PerformanceAssessment(Base):
    __tablename__ = "performance_assessments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    evaluation_type = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=False)
    overlapping_tasks = Column(Integer, default=0)

    actual_time_spent = Column(Float, nullable=True)
    user_stress_score = Column(Float, nullable=True)

    subject = relationship("Subject", back_populates="assessments")
