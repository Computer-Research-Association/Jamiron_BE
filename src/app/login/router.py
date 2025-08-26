# src/app/login/router.py
import logging
from fastapi import APIRouter, Depends, logger
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.app.config.database import get_db # get_db 함수 임포트
from src.app.login.service import get_syllabus_collector, SyllabusCollector

#from src.app.login.service import SyllabusCollector

router = APIRouter()

# 요청 바디의 데이터 구조를 정의
class LoginAndScrapeRequest(BaseModel):
    user_id: str
    password: str
    year: str
    semester: str

@router.post("/")
async def login_and_scrape(
    credentials: LoginAndScrapeRequest,
    db: Session = Depends(get_db), # 데이터베이스 세션을 주입
    collector: SyllabusCollector = Depends(get_syllabus_collector)
):
    """
    사용자 로그인, 강의 계획서 페이지 이동,
    강의 계획서 데이터 크롤링 및 데이터베이스 저장을 처리합니다.
    """
    # logger = logging.getLogger(__name__)
    # logger.info(f"📥 로그인 요청: {credentials.user_id}, {credentials.year}-{credentials.semester}")
    # logger.info("🔍 강의 계획서 크롤링 시작...")



    try:
        # 1단계: 히즈넷 로그인
        if not collector.login(credentials.user_id, credentials.password):
            return {"status": 401, "message": "로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요."}

        # 2단계: 올바른 강의 계획서 페이지로 이동
        if not collector.navigate_to_planner_page(credentials.year, credentials.semester):
            return {"status": 404, "message": f"지정된 학년/학기({credentials.year}-{credentials.semester})에 대한 강의 계획서 페이지를 찾을 수 없습니다."}
            
        # 3단계: 강의 계획서 데이터를 크롤링하고 데이터베이스에 저장
        # download_planners 메서드는 이제 'db' 세션이 필요합니다.
        collector.download_planners()
        collected_syllabuses_details = collector.get_collected_syllabuses()

        return {
            "status": 200,
            "message": "강의 계획서 크롤링 및 데이터베이스 저장 성공.",
            "syllabuses": collected_syllabuses_details
        }


    except Exception as e:
        # 일반적인 오류 처리
        return {"status": 500, "message": f"예상치 못한 오류가 발생했습니다: {str(e)}"}
        
    finally:
        # 4단계: 작업 완료 후 반드시 웹 드라이버를 종료
        collector.close()