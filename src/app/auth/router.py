# domain/auth/router.py
from fastapi import Header, APIRouter, Depends
from src.app.auth.session_factory import delete_session, require_session
from src.app.user.dto import User
from src.app.auth.service import authenticate_and_create_session


router = APIRouter()

@router.post("/login")
def login(req: User):
    session_id = authenticate_and_create_session(req)
    return {"status": 200, "message": "로그인 성공.", "session_id": session_id}

@router.post("/logout")
def logout(session_id: str | None = Header(default=None, convert_underscores=False)):
    if session_id:
        delete_session(session_id)
    return {"status": 200, "message": "로그아웃 성공."}

@router.get("/me")
def me(session_id: str | None = Header(default=None, convert_underscores=False)):
    require_session(session_id)
    return {"status": 200, "message": "인증 성공"}
