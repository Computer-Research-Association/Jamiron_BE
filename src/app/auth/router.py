# domain/auth/router.py
from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel, SecretStr
from src.app.session.redis_client import redis
from src.app.session.service import new_token, create_session, get_session, delete_session

router = APIRouter()

# 데모용. 실제는 DB의 해시된 비밀번호 비교 + (필요시) 학교 로그인 검증
FAKE = {"test": "$dummy$"}  # 존재 여부만 체크한다고 가정

class LoginIn(BaseModel):
    username: str
    password: SecretStr

class LoginOut(BaseModel):
    session_token: str
    expires_in: int = 7 * 24 * 3600

@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, res: Response):
    if body.username not in FAKE:
        raise HTTPException(401, "Invalid credentials")

    token = new_token()
    # 실제 user_id는 DB에서 조회한 PK
    await create_session(redis, token, user_id=123)
    # 프로그램 환경이라 쿠키 대신 헤더/바디로 토큰을 전달
    return LoginOut(session_token=token)

@router.post("/logout")
async def logout(x_session_token: str | None = Header(default=None, convert_underscores=False)):
    if x_session_token:
        await delete_session(redis, x_session_token)
    return {"ok": True}
