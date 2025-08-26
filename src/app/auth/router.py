# domain/auth/router.py
from fastapi import Header
from src.app.auth.session_factory import delete_session
from src.app.auth.service import login
from src.app.user.dto import User


router = APIRouter()

@router.post("/login", response_model=LoginOut)
async def login(req:User):
    token = await login(req)
    return token

@router.post("/logout")
async def logout(x_session_token: str | None = Header(default=None, convert_underscores=False)):
    if x_session_token:
        await delete_session(x_session_token)
    return {"ok": True}