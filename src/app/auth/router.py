# domain/auth/router.py
from fastapi import Header, APIRouter
from src.app.auth.session_factory import delete_session
from src.app.auth.service import login
from src.app.user.dto import User


router = APIRouter()

@router.post("/login")
async def authenticate_and_create_session(req:User):
    session_id = await login(req)
    return {"status": 200,
            "message": "로그인 성공.",
            "session_id": session_id}

@router.post("/logout")
async def logout(session_id: str | None = Header(default=None, convert_underscores=False)):
    if session_id:
        await delete_session(session_id)
    return {"status": 200,
            "message": "로그아웃 성공."}