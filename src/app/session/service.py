# infra/security.py
import uuid, time
from typing import Dict
from fastapi import Header, HTTPException
from redis.asyncio import Redis
from src.app.config.settings import settings

redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)

def now() -> int: return int(time.time())

def new_token() -> str: return uuid.uuid4().hex

async def create_session(token: str, user_id: int):
    key = f"sess:{token}"
    await redis.hset(key, mapping={"user_id": str(user_id), "issued_at": str(now())})
    await redis.expire(key, SESSION_TTL)

async def get_session(token: str) -> Dict[str, str]:
    sess = await redis.hgetall(f"sess:{token}")
    if not sess:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return sess

async def delete_session(token: str):
    await redis.delete(f"sess:{token}")

async def require_session(x_session_token: str | None = Header(default=None, convert_underscores=False)) -> int:
    if not x_session_token:
        raise HTTPException(401, "Missing X-Session-Token")
    sess = await get_session(x_session_token)
    try:
        return int(sess['user_id'])
    except (KeyError, ValueError):
        await delete_session(x_session_token)
        raise HTTPException(401, "Invalid session payload")
