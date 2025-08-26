from fastapi import APIRouter, Depends
from src.app.auth.session_factory import require_session

router = APIRouter()

@router.get("/me")
async def me(user_id: int = Depends(require_session)):
    # 여기서 DB/캐시로 과목·권한 조회 (필요시 5~10분 캐시)
    return {"user_id": user_id, "courses": []}