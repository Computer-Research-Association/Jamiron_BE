from fastapi import APIRouter, Depends
from src.app.auth.session_factory import require_session

import logging
from fastapi import APIRouter, Depends, HTTPException  # HTTPException 사용을 위해 임포트
from pydantic import BaseModel
from sqlalchemy.orm import Session
# ..config.database에서 get_db만 임포트합니다. Base는 model.py에서 관리합니다.
from ..config.database import get_db

# service 모듈 임포트
from . import service as user_service  # user_service로 별칭을 지정하여 사용

logger = logging.getLogger(__name__)
router = APIRouter()

# 요청 바디의 데이터 구조를 정의
# syllabuses 딕셔너리 안에 실제 강의 정보가 들어갈 것으로 예상됩니다.
class UserDate(BaseModel):
    user_id: str
    class_code: str
    professor_name: str# 학기별 강의 목록을 담는 딕셔너리
    year: str
    semester: str


# 새로운 사용자 데이터 (강의 계획서 데이터 포함)를 생성 또는 업데이트하는 엔드포인트
@router.post("/")
async def create_or_update_user_syllabus_data(
        user_data: UserDate,
        db: Session = Depends(get_db)
):
    """
    사용자의 학년/학기에 대한 강의 계획서 데이터를 생성하거나 업데이트합니다.
    """
    logger.info(
        f"💾 사용자 강의 데이터 요청: User ID: {user_data.user_id}, Year: {user_data.year}, Semester: {user_data.semester}")

    try:
        # 서비스 계층의 함수를 호출하여 데이터 저장 로직을 처리
        # user_service.create_or_update_user_syllabuses 함수가 UserDate 객체를 받아 처리하도록 가정
        db_data = user_service.create_or_update_user_syllabuses(db, user_data)

        return {
            "status": 200,
            "message": "사용자 강의 계획서 데이터 처리 성공.",
            "data": db_data  # 저장되거나 업데이트된 데이터 반환
        }
    except ValueError as e:
        logger.warning(f"⚠️ 사용자 강의 데이터 처리 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 사용자 강의 데이터 처리 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}")


# 특정 사용자의 모든 강의 계획서 데이터를 조회하는 엔드포인트
@router.get("/{user_id}")
async def get_user_all_syllabuses(user_id: str, db: Session = Depends(get_db)):
    """
    특정 사용자의 모든 연도/학기별 강의 계획서 데이터를 조회합니다.
    """
    logger.info(f"🔍 사용자 강의 데이터 조회 요청: User ID: {user_id}")

    try:
        # 서비스 계층의 함수를 호출하여 데이터 조회 로직을 처리
        # user_service.get_user_syllabuses_by_user_id 함수가 user_id를 받아 처리하도록 가정
        user_syllabuses = user_service.get_user_syllabuses_by_user_id(db, user_id)

        if not user_syllabuses:
            raise HTTPException(status_code=404, detail=f"User ID '{user_id}'에 대한 강의 데이터를 찾을 수 없습니다.")

        return {
            "status": 200,
            "message": f"User ID '{user_id}'의 강의 데이터 조회 성공.",
            "data": user_syllabuses  # 조회된 데이터 반환
        }
    except HTTPException as e:
        raise e  # 404 예외는 그대로 다시 발생시킵니다.
    except Exception as e:
        logger.error(f"❌ 사용자 강의 데이터 조회 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류가 발생했습니다: {str(e)}")

