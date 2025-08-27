import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List, Dict, Any
from src.app.model import UserSyllabusData, Syllabus  # 모델 임포트

logger = logging.getLogger(__name__)

# Pydantic 모델
class UserDate(BaseModel):
    user_id: str
    syllabuses: Dict[str, str]  # {class_code: professor_name}
    year: str
    semester: str

def create_or_update_user_syllabuses(db: Session, user_data: UserDate) -> List[Dict[str, Any]]:
    """
    UserDate 모델의 데이터를 기반으로 사용자의 학기별, 강의별 데이터를
    생성하거나 업데이트합니다.
    """
    logger.info(f"서비스: 사용자 강의 데이터 처리 시작 - User ID: {user_data.user_id}")

    results = []

    # syllabuses 딕셔너리를 순회하며 처리
    for class_code, professor_name in user_data.syllabuses.items():
        db_entry = db.query(UserSyllabusData).filter(
            UserSyllabusData.user_id == user_data.user_id,
            UserSyllabusData.year == user_data.year,
            UserSyllabusData.semester == user_data.semester,
            UserSyllabusData.class_code == class_code
        ).first()

        try:
            if db_entry:
                # 기존 데이터가 있으면 교수명 업데이트
                logger.info(f"서비스: 기존 강의 데이터 업데이트 - ID: {db_entry.id}")
                db_entry.professor_name = professor_name
                db.commit()
                db.refresh(db_entry)
            else:
                # 새로운 데이터 생성
                logger.info(f"서비스: 새로운 강의 데이터 생성 - Class Code: {class_code}")
                new_entry = UserSyllabusData(
                    user_id=user_data.user_id,
                    year=user_data.year,
                    semester=user_data.semester,
                    class_code=class_code,
                    professor_name=professor_name
                )
                db.add(new_entry)
                db.commit()
                db.refresh(new_entry)
                db_entry = new_entry

            # 처리된 데이터 리스트에 추가
            results.append({
                "id": db_entry.id,
                "user_id": db_entry.user_id,
                "year": db_entry.year,
                "semester": db_entry.semester,
                "class_code": db_entry.class_code,
                "professor_name": db_entry.professor_name
            })

        except IntegrityError:
            db.rollback()
            logger.error(
                f"서비스: 데이터 무결성 오류 발생 - User ID: {user_data.user_id}, Class Code: {class_code}")
            raise ValueError(f"중복 데이터 존재: user_id={user_data.user_id}, year={user_data.year}, semester={user_data.semester}, class_code={class_code}")
        except Exception as e:
            db.rollback()
            logger.error(f"서비스: 강의 데이터 처리 중 예상치 못한 오류 - {str(e)}", exc_info=True)
            raise e

    return results

'''
def get_user_syllabuses(db: Session, user_id: str, year: str, semester: str) -> List[Dict[str, Any]]:
    """
    user_syllabus_data에서 사용자의 강의 정보를 찾고,
    학년(year)와 학기(semester) 기준으로 syllabuses 테이블의 강의 계획서와 매칭합니다.
    """
    # 특정 학년/학기만 조회
    user_courses = db.query(UserSyllabusData).filter(
        UserSyllabusData.user_id == user_id,
        UserSyllabusData.year == year,
        UserSyllabusData.semester == semester
    ).all()

    if not user_courses:
        return []

    results = []

    for course in user_courses:
        matching_syllabus = db.query(Syllabus).filter(
            Syllabus.class_code == course.class_code,
            Syllabus.year == course.year,
            Syllabus.semester == course.semester  # DB 컬럼이 semester로 되어 있어야 함
        ).first()

        if matching_syllabus:
            results.append({
                "user_id": course.user_id,
                "class_code": course.class_code,
                "year": course.year,
                "semester": course.semester,
                "professor_name": course.professor_name,
                "syllabus_description": matching_syllabus.description,
                "syllabus_objectives": matching_syllabus.objectives,
                "syllabus_schedule": matching_syllabus.schedule
            })

    return results
'''