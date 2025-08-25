# domain/auth/router.py
from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel, SecretStr
from src.app.session.service import delete_session, require_session
from fastapi import APIRouter, Depends
from src.app.auth.service import login


router = APIRouter()

# 데모용. 실제는 학교 로그인 검증. 로그인으로 성공을 받아오면 ok

class LoginIn(BaseModel):
    username: str
    password: SecretStr

class LoginOut(BaseModel):
    session_token: str

@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, res: Response):
    await login(body, res)

@router.post("/logout")
async def logout(x_session_token: str | None = Header(default=None, convert_underscores=False)):
    if x_session_token:
        await delete_session(x_session_token)
    return {"ok": True}

router = APIRouter()

@router.get("/me")
async def me(user_id: int = Depends(require_session)):
    # 여기서 DB/캐시로 과목·권한 조회 (필요시 5~10분 캐시)
    return {"user_id": user_id, "courses": []}