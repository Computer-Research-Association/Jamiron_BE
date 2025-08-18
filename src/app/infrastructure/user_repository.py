# 인프라 (DB 접근 / 외부 의존성)
from src.app.domain.user import User

class UserRepository:
    def __init__(self):
        # 임시 DB 흉내 (나중에 Postgres, SQLAlchemy로 교체)
        self.users = {
            1: User(id=1, name="Alice"),
            2: User(id=2, name="Bob"),
        }

    def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)
