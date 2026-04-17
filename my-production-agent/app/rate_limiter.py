import time
from fastapi import HTTPException
import redis
from .config import settings

# Initialize Redis client with robust options for cloud proxies
r = redis.from_url(
    settings.get_redis_url(),
    decode_responses=True,          # Automatically decode bytes to str
    health_check_interval=30,       # Keep connection alive
    socket_connect_timeout=10,      # Avoid hanging on connection
    retry_on_timeout=True,
)

async def check_rate_limit(api_key: str):
    """
    Redis-based rate limiting (Fixed Window).
    """
    user_id = api_key[:8]
    minute_key = f"rate_limit:{user_id}:{int(time.time() // 60)}"
    
    try:
        current_count = r.get(minute_key)
        
        if current_count and int(current_count) >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            )
        
        pipe = r.pipeline()
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)
        pipe.execute()
        
    except redis.RedisError as e:
        # Pass logs or handle accordingly
        pass
