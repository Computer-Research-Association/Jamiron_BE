# FastAPI 라우터 (입출력 처리)
from fastapi import APIRouter, Depends
from src.app.application.user_service import UserService
from src.app.infrastructure.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service():
    return UserService(UserRepository())

@router.get("/{user_id}")
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    if not user:
        return {"error": "User not found"}
    return {"id": user.id, "name": user.name}
