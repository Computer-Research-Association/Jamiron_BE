import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Dict, Any

from ..model import UserSyllabusData  # 이 부분을 추가해야 합니다.


# Pydantic 모델을 파일 상단에 정의하거나 import하세요.
class UserDate(BaseModel):
    user_id: str
    class_code: str
    professor_name: str
    year: str
    semester: str

# 데이터베이스 모델도 새로운 구조에 맞게 변경되어야 합니다.
# from ..model import UserSyllabusData

logger = logging.getLogger(__name__)

def create_or_update_user_syllabuses(db: Session, user_data: UserDate) -> Dict[str, Any]:
    """
    UserDate 모델의 데이터를 기반으로 사용자의 학기별, 강의별 데이터를
    생성하거나 업데이트합니다.
    """
    logger.info(f"서비스: 사용자 강의 데이터 처리 시작 - User ID: {user_data.user_id}, Class Code: {user_data.class_code}")

    # 1. user_id, year, semester, class_code를 기준으로 기존 데이터가 있는지 확인
    db_entry = db.query(UserSyllabusData).filter(
        UserSyllabusData.user_id == user_data.user_id,
        UserSyllabusData.year == user_data.year,
        UserSyllabusData.semester == user_data.semester,
        UserSyllabusData.class_code == user_data.class_code
    ).first()

    try:
        if db_entry:
            # 2. 기존 데이터가 있으면 교수명 업데이트
            logger.info(f"서비스: 기존 강의 데이터 업데이트 - ID: {db_entry.id}")
            db_entry.professor_name = user_data.professor_name
            db.commit()
            db.refresh(db_entry)
        else:
            # 3. 새로운 데이터 생성
            logger.info("서비스: 새로운 강의 데이터 생성")
            new_entry = UserSyllabusData(
                user_id=user_data.user_id,
                year=user_data.year,
                semester=user_data.semester,
                class_code=user_data.class_code,
                professor_name=user_data.professor_name
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
            db_entry = new_entry

        # 4. 처리된 데이터를 딕셔너리 형태로 반환
        return {
            "id": db_entry.id,
            "user_id": db_entry.user_id,
            "year": db_entry.year,
            "semester": db_entry.semester,
            "class_code": db_entry.class_code,
            "professor_name": db_entry.professor_name
        }

    except IntegrityError:
        db.rollback()
        logger.error(
            f"서비스: 데이터 무결성 오류 발생 - User ID: {user_data.user_id}, Class Code: {user_data.class_code}")
        raise ValueError("동일한 사용자, 연도, 학기에 대한 강의 데이터가 이미 존재합니다.")
    except Exception as e:
        db.rollback()
        logger.error(f"서비스: 강의 데이터 처리 중 예상치 못한 오류 - {str(e)}", exc_info=True)
        raise e