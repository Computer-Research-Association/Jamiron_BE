# domain/auth/router.py
from fastapi import APIRouter, HTTPException, Header, Response
from src.app.session.service import delete_session, require_session
from fastapi import APIRouter, Depends
from src.app.auth.service import login
from src.app.auth.dto import LoginIn, LoginOut


router = APIRouter()

@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, res: Response):
    token = await login(body, res)
    return LoginOut(session_token=token)

@router.post("/logout")
async def logout(x_session_token: str | None = Header(default=None, convert_underscores=False)):
    if x_session_token:
        await delete_session(x_session_token)
    return {"ok": True}

@router.get("/me")
async def me(user_id: int = Depends(require_session)):
    # 여기서 DB/캐시로 과목·권한 조회 (필요시 5~10분 캐시)
    return {"user_id": user_id, "courses": []}d