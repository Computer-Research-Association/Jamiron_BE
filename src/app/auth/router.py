from fastapi import Header, APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.auth.session_factory import delete_session, optional_session
from src.app.user.dto import User
from src.app.auth.service import authenticate_and_create_session
from src.app.syllabus.service import SyllabusCollector, get_syllabus_collector
from src.app.config.database import get_db

router = APIRouter()


@router.post("/login")
def login(
    req: User,
    collector: SyllabusCollector = Depends(get_syllabus_collector),
    db: Session = Depends(get_db)
):
    session_id = authenticate_and_create_session(req, db, collector)
    return {"status": 200, "message": "로그인 성공.", "session_id": session_id}

@router.post("/logout")
def logout(session_id: str | None = Header(default=None, convert_underscores=False)):
    if session_id:
        delete_session(session_id)
    return {"status": 200, "message": "로그아웃 성공."}

@router.get("/session-check")
async def session_check(user_name: str | None = Depends(optional_session)):
    if user_name:
        return {"status": 200, "message": "이미 로그인됨"}
    return {"status": 204, "message": "세션 없음"}