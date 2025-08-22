from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import uuid
router = APIRouter()

class LoginInput(BaseModel):
    userid: str
    password: str
class LoginOutput(BaseModel):
    session_token: str

sessions = {}

# 데모용 사용자 (DB 대신 하드코딩)
FAKE_USER = {
    "id": "testuser",
    "pw": "1234"
}

@router.post("/api/login")
async def login(body: LoginInput):
    print(body.userid)
    print(body.password)
    if body.username != FAKE_USER["id"] or body.password != FAKE_USER["pw"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = uuid.uuid4().hex
    sessions[token] = {"user": body.username}

    return LoginOutput(session_token=token)

#  DB에 저장
#  검증