# 유스케이스 (도메인 규칙 사용)
from src.app.domain.user import User

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> User:
        return self.user_repository.get_by_id(user_id)
