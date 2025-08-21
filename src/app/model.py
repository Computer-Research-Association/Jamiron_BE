from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Syllabus(Base):
    __tablename__ = "syllabuses"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(255), nullable=False)
    class_code = Column(String(50), nullable=False)
    professor_name = Column(String(100))
    prof_email = Column(String(255))
    year = Column(String(10), nullable=False)
    hakgi = Column(String(10), nullable=False)
    objectives = Column(Text)
    description = Column(Text)
    schedule = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 수강생들과의 관계
    enrollments = relationship("UserEnrollment", back_populates="syllabus")


class UserEnrollment(Base):
    """사용자가 수강하는 강의 정보를 저장하는 테이블"""
    __tablename__ = "user_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)  # 히즈넷 학번/교번
    class_code = Column(String(50), nullable=False)
    year = Column(String(10), nullable=False)
    hakgi = Column(String(10), nullable=False)
    syllabus_id = Column(Integer, ForeignKey("syllabuses.id"), nullable=True)  # 실라버스 테이블과 연결
    enrolled_at = Column(DateTime, default=datetime.now)

    # 실라버스와의 관계
    syllabus = relationship("Syllabus", back_populates="enrollments")

    # 중복 수강 방지를 위한 유니크 제약조건
    __table_args__ = (
        UniqueConstraint('user_id', 'class_code', 'year', 'hakgi', name='unique_user_enrollment'),
    )
