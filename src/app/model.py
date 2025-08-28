from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Syllabus(Base):
    __tablename__ = "syllabuses"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(255), nullable=False)
    class_code = Column(String(50), nullable=False)
    class_division = Column(String(10), nullable=False)
    professor_name = Column(String(100))
    prof_email = Column(String(255))
    year = Column(String(10), nullable=False)
    semester = Column(String(10), nullable=False)
    objectives = Column(Text)
    description = Column(Text)
    schedule = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class UserSyllabusData(Base):
    __tablename__ = "user_syllabus_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    class_code = Column(String(50), nullable=False)         # 길이를 Syllabus와 맞춤
    class_division = Column(String(10), nullable=False)
    year = Column(String(10), nullable=False)
    semester = Column(String(10), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'year',
            'semester',
            'class_code',
            'class_division',   # 분반도 고유성 조건에 포함
            name='uq_user_year_semester_code_division'
        ),
    )

class User_Id(Base):
    __tablename__ = "user_Id"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
