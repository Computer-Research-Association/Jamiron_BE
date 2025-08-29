import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List, Dict, Any
from src.app.model import UserSyllabusData, Syllabus  # 모델 임포트

logger = logging.getLogger(__name__)

class UserDate(BaseModel):
    username: str
    syllabuses: Dict[str, str]
    year: str
    semester: str

def create_or_update_user_syllabuses(db: Session, user_data: UserDate) -> List[Dict[str, Any]]:
    logger.info(f"서비스: 사용자 강의 데이터 처리 시작 - User ID: {user_data.username}")

    results = []

    # syllabuses 딕셔너리를 순회하며 처리
    for class_code, class_division in user_data.syllabuses.items():
        db_entry = db.query(UserSyllabusData).filter(
            UserSyllabusData.username == user_data.username,
            UserSyllabusData.year == user_data.year,
            UserSyllabusData.semester == user_data.semester,
            UserSyllabusData.class_code == class_code,
            UserSyllabusData.class_division == class_division

        ).first()

        try:
            if db_entry:
                logger.info(f"서비스: 기존 데이터 존재 - ID: {db_entry.id}, 건너뜀")
            else:
                # 새로운 데이터 생성
                logger.info(f"서비스: 새로운 강의 데이터 생성 - Class Code: {class_code}")
                new_entry = UserSyllabusData(
                    username=user_data.username,
                    year=user_data.year,
                    semester=user_data.semester,
                    class_code=class_code,
                    class_division=class_division
                )
                db.add(new_entry)
                db.commit()
                db.refresh(new_entry)
                db_entry = new_entry

            results.append({
                "id": db_entry.id,
                "username": db_entry.username,
                "year": db_entry.year,
                "semester": db_entry.semester,
                "class_code": db_entry.class_code,
                "class_division": db_entry.class_division
            })

        except IntegrityError:
            db.rollback()
            logger.error(
                f"서비스: 데이터 무결성 오류 발생 - User ID: {user_data.username}, Class Code: {class_code}")
            raise ValueError(f"중복 데이터 존재: username={user_data.username}, year={user_data.year}, semester={user_data.semester}, class_code={class_code}")
        except Exception as e:
            db.rollback()
            logger.error(f"서비스: 강의 데이터 처리 중 예상치 못한 오류 - {str(e)}", exc_info=True)
            raise e

    return results
