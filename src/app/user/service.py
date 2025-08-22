import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List, Dict, Any  # Dict, Any 타입 힌트 추가

# model.py에 UserSyllabusData 모델이 정의되어 있다고 가정합니다.
from ..model import UserSyllabusData


# 라우터에서 정의된 UserDate Pydantic 모델을 임포트합니다.
# 직접 정의하는 대신 임포트하여 일관성을 유지합니다.
# from ..user.router import UserDate # <--- 순환 참조를 피하기 위해 직접 정의하거나 다른 유틸리티 파일에서 정의하는 것이 좋습니다.
# 여기서는 사용자가 제공한 UserDate 정의를 그대로 사용합니다.
class UserDate(BaseModel):
    user_id: str
    syllabuses: Dict[str, Any]  # 딕셔너리 내부 타입은 Any로 유연하게 처리
    year: str
    semester: str


logger = logging.getLogger(__name__)


def create_or_update_user_syllabuses(db: Session, user_data: UserDate) -> Dict[str, Any]:
    """
    UserDate 모델의 데이터를 기반으로 사용자의 학기별 강의 계획서 데이터를
    생성하거나 업데이트합니다.
    """
    logger.info(
        f"서비스: 사용자 강의 데이터 처리 시작 - User ID: {user_data.user_id}, Year: {user_data.year}, Semester: {user_data.semester}")

    # 기존 데이터가 있는지 확인
    db_entry = db.query(UserSyllabusData).filter(
        UserSyllabusData.user_id == user_data.user_id,
        UserSyllabusData.year == user_data.year,
        UserSyllabusData.semester == user_data.semester
    ).first()

    try:
        if db_entry:
            # 기존 데이터가 있으면 업데이트
            logger.info(f"서비스: 기존 강의 데이터 업데이트 - ID: {db_entry.id}")
            db_entry.syllabuses = user_data.syllabuses  # @syllabuses.setter 호출
            db.commit()
            db.refresh(db_entry)

            # 업데이트된 데이터 반환
            return {
                "id": db_entry.id,
                "user_id": db_entry.user_id,
                "year": db_entry.year,
                "semester": db_entry.semester,
                "syllabuses": db_entry.syllabuses  # @syllabuses.getter 호출
            }
        else:
            # 새로운 데이터 생성
            logger.info("서비스: 새로운 강의 데이터 생성")
            new_entry = UserSyllabusData(
                user_id=user_data.user_id,
                year=user_data.year,
                semester=user_data.semester,
                syllabuses=user_data.syllabuses  # @syllabuses.setter 호출
            )
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)

            # 생성된 데이터 반환
            return {
                "id": new_entry.id,
                "user_id": new_entry.user_id,
                "year": new_entry.year,
                "semester": new_entry.semester,
                "syllabuses": new_entry.syllabuses  # @syllabuses.getter 호출
            }
    except IntegrityError:
        db.rollback()
        logger.error(
            f"서비스: 데이터 무결성 오류 발생 - User ID: {user_data.user_id}, Year: {user_data.year}, Semester: {user_data.semester}")
        raise ValueError("동일한 사용자, 연도, 학기에 대한 강의 데이터가 이미 존재합니다.")
    except Exception as e:
        db.rollback()
        logger.error(f"서비스: 강의 데이터 처리 중 예상치 못한 오류 - {str(e)}", exc_info=True)
        raise e


def get_user_syllabuses_by_user_id(db: Session, user_id: str) -> List[Dict[str, Any]]:
    """
    특정 user_id에 해당하는 모든 연도/학기별 강의 계획서 데이터를 조회합니다.
    """
    logger.info(f"서비스: 사용자 강의 데이터 조회 시작 - User ID: {user_id}")
    db_entries = db.query(UserSyllabusData).filter(UserSyllabusData.user_id == user_id).all()

    if not db_entries:
        logger.info(f"서비스: User ID '{user_id}'에 대한 강의 데이터 없음.")
        return []

    # 조회된 DB 객체들을 딕셔너리 리스트로 변환하여 반환
    results = [
        {
            "id": entry.id,
            "user_id": entry.user_id,
            "year": entry.year,
            "semester": entry.semester,
            "syllabuses": entry.syllabuses  # @syllabuses.getter 호출
        }
        for entry in db_entries
    ]
    logger.info(f"서비스: User ID '{user_id}'에 대한 {len(results)}개의 강의 데이터 조회 완료.")
    return results

