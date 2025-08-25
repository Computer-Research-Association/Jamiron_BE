# domain/auth/router.py
from fastapi import APIRouter, HTTPException, Header, Response
from pydantic import BaseModel, SecretStr
from src.app.session.redis_client import redis
from src.app.session.service import new_token, create_session, get_session, delete_session
from src.app.syllabus.service import SyllabusCollector
from fastapi import APIRouter, Depends
from src.app.auth.router import require_session


router = APIRouter()

# 데모용. 실제는 학교 로그인 검증. 로그인으로 성공을 받아오면 ok

class LoginIn(BaseModel):
    username: str
    password: SecretStr

class LoginOut(BaseModel):
    session_token: str

@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, res: Response):
    collector = SyllabusCollector()
    if not collector.login(LoginIn.user_id, LoginIn.password.get_secret_value()):
        # 로그인 시도 실패하면 실패 반환
        raise HTTPException (401,"로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")
    # 로그인 시도 성공하면 아이디만 db에 저장

    # 토큰 발급. 고유한 id
    token = new_token()
    # 실제 user_id는 DB에서 조회한 PK 아무튼 redis에 user id랑 고유한 토큰 id 전달
    await create_session(redis, token, user_id=123)
    # 프로그램 환경이라 쿠키 대신 헤더/바디로 토큰을 전달
    return LoginOut(session_token=token)

@router.post("/logout")
async def logout(x_session_token: str | None = Header(default=None, convert_underscores=False)):
    if x_session_token:
        await delete_session(redis, x_session_token)
    return {"ok": True}

router = APIRouter()

@router.get("/me")
async def me(user_id: int = Depends(require_session)):
    # 여기서 DB/캐시로 과목·권한 조회 (필요시 5~10분 캐시)
    return {"user_id": user_id, "courses": []}