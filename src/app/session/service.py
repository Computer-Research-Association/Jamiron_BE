# infra/security.py
import uuid, time
from fastapi import HTTPException

SESSION_TTL = 7 * 24 * 3600         # 7일 (idle)

def now() -> int: return int(time.time())

def new_token() -> str: return uuid.uuid4().hex

async def create_session(redis, token: str, user_id: int):
    await redis.hset(f"sess:{token}", mapping={"user_id": str(user_id), "issued_at": str(now())})
    await redis.expire(f"sess:{token}", SESSION_TTL)

async def get_session(redis, token: str) -> dict:
    sess = await redis.hgetall(f"sess:{token}")
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

async def delete_session(redis, token: str):
    await redis.delete(f"sess:{token}")
