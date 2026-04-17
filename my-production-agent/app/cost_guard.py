import time
from fastapi import HTTPException
import redis
from .config import settings

# Initialize Redis client with robust options for cloud proxies
r = redis.from_url(
    settings.get_redis_url(),
    decode_responses=True,
    health_check_interval=30,
    socket_connect_timeout=10,
    retry_on_timeout=True,
)

async def check_budget(api_key: str, estimated_cost: float = 0.001):
    """
    Redis-based Cost Guard.
    """
    user_id = api_key[:8]
    month_key = f"budget:{user_id}:{time.strftime('%Y-%m')}"
    
    try:
        current_spending = r.get(month_key)
        
        if current_spending and float(current_spending) + estimated_cost > settings.monthly_budget_usd:
            raise HTTPException(
                status_code=402,
                detail=f"Monthly budget exhausted: ${settings.monthly_budget_usd}",
            )
        
        r.incrbyfloat(month_key, estimated_cost)
        r.expire(month_key, 32 * 24 * 3600)
        
    except redis.RedisError:
        pass
