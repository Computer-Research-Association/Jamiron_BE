from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# Base를 직접 import하지 말고, 여기서 새로 정의하거나
# 또는 database.py에서만 models를 import하도록 변경
Base = declarative_base()

class Syllabus(Base):
    __tablename__ = "syllabuses"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(255), index=True)
    class_code = Column(String(50), index=True)
    professor_name = Column(String(100))
    prof_email = Column(String(100))
    year = Column(String(10))
    hakgi = Column(String(10))
    # MySQL의 경우 긴 텍스트는 Text 타입 사용
    objectives = Column(Text)
    description = Column(Text)
    schedule = Column(Text)