# 도메인 엔티티 (비즈니스 규칙)
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
