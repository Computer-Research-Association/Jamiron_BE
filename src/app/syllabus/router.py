from fastapi import APIRouter, Depends, logger
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.app.config.database import get_db
from src.app.syllabus.service import get_syllabus_collector, SyllabusCollector
from src.app.auth.session_factory import require_session


router = APIRouter()

class LoginAndScrapeRequest(BaseModel):
    user_id: str
    password: str
    year: str
    semester: str

@router.post("/")
async def login_and_scrape(
    credentials: LoginAndScrapeRequest,
    collector: SyllabusCollector = Depends(get_syllabus_collector),
    db: Session = Depends(get_db),
    session_id: str = Depends(require_session)
):

    try:
        if not collector.login(credentials.user_id, credentials.password):
            return {"status": 401, "message": "로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요."}

        if not collector.navigate_to_planner_page(credentials.year, credentials.semester):
            return {"status": 404, "message": f"지정된 학년/학기({credentials.year}-{credentials.semester})에 대한 강의 계획서 페이지를 찾을 수 없습니다."}

        collector.download_planners()
        collected_syllabuses_details = collector.get_collected_syllabuses()

        return {
            "status": 200,
            "message": "강의 계획서 크롤링 및 데이터베이스 저장 성공.",
            "syllabuses": collected_syllabuses_details
        }


    except Exception as e:
        return {"status": 500, "message": f"예상치 못한 오류가 발생했습니다: {str(e)}"}

    finally:
        collector.close()