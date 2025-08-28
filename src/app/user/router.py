import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.app.config.database import get_db
from src.app.user import service as user_service  # user_service로 별칭 지정

logger = logging.getLogger(__name__)
router = APIRouter()

class UserDate(BaseModel):
    user_id: str
    syllabuses: Dict[str, str]  # key=class_code, value=class_division
    year: str
    semester: str


@router.post("/")
async def create_or_update_user_syllabus_data(
        user_data: UserDate,
        db: Session = Depends(get_db)
):
    logger.info(
        f"사용자 강의 데이터 요청: User ID: {user_data.user_id}, Year: {user_data.year}, Semester: {user_data.semester}"
    )

    try:
        db_data = user_service.create_or_update_user_syllabuses(db, user_data)

        return {
            "status": 200,
            "message": "사용자 강의 계획서 데이터 처리 성공.",
            "data": db_data
        }
    except ValueError as e:
        logger.warning(f"사용자 강의 데이터 처리 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"사용자 강의 데이터 처리 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}")
