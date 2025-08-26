import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..config.database import get_db
from ..user.service import get_user_syllabuses
from . import service as user_service  # user_service로 별칭 지정

logger = logging.getLogger(__name__)
router = APIRouter()


# 요청 바디 모델: syllabuses 딕셔너리 {class_code: professor_name}
class UserDate(BaseModel):
    user_id: str
    syllabuses: Dict[str, str]  # key=class_code, value=professor_name
    year: str
    semester: str


# 새로운 사용자 데이터 생성 또는 업데이트
@router.post("/")
async def create_or_update_user_syllabus_data(
        user_data: UserDate,
        db: Session = Depends(get_db)
):
    """
    사용자의 학년/학기에 대한 강의 계획서 데이터를 생성하거나 업데이트합니다.
    syllabuses 딕셔너리를 순회하며 여러 강의 처리 가능.
    """
    logger.info(
        f"💾 사용자 강의 데이터 요청: User ID: {user_data.user_id}, Year: {user_data.year}, Semester: {user_data.semester}"
    )

    try:
        # 서비스 계층 함수 호출: 여러 강의 처리 가능
        db_data = user_service.create_or_update_user_syllabuses(db, user_data)

        return {
            "status": 200,
            "message": "사용자 강의 계획서 데이터 처리 성공.",
            "data": db_data  # 처리된 강의 데이터 리스트
        }
    except ValueError as e:
        logger.warning(f"⚠️ 사용자 강의 데이터 처리 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 사용자 강의 데이터 처리 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}")


# 특정 사용자의 강의 계획서 조회
@router.get("/users", response_model=List[Dict[str, Any]])
def read_user_syllabuses(
        user_id: str,
        year: str,
        semester: str,
        db: Session = Depends(get_db)
):
    """
    특정 사용자의 수강 과목과 매칭되는 강의 계획서 데이터를 조회합니다.
    """
    syllabuses = get_user_syllabuses(db, user_id, year, semester)

    if not syllabuses:
        raise HTTPException(
            status_code=404,
            detail=f"User ID '{user_id}', Year '{year}', Semester '{semester}'에 대한 강의 계획서를 찾을 수 없습니다."
        )

    return syllabuses
