import time
import json
import signal
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit, r as redis_client
from .cost_guard import check_budget
from .logger import setup_logging
from .services.llm_service import gemini_service

# Setup structured logging
logger = setup_logging(logging.DEBUG if settings.debug else logging.INFO)

START_TIME = time.time()
_is_ready = False

# ─────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info("Initializing application services...")
    
    # Debug: Print masked Redis URL to verify env var loading
    url = settings.get_redis_url()
    redis_masked = url.split('@')[-1] if '@' in url else url
    logger.info(f"Connecting to Redis at: ...@{redis_masked}")

    # Check Redis connection
    try:
        redis_client.ping()
        logger.info("Redis connection established.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # In production, we might want to shut down if Redis is critical
    
    _is_ready = True
    logger.info(f"Agent '{settings.app_name}' is ready on {settings.host}:{settings.port}")
    
    yield
    
    _is_ready = False
    logger.info("Shutting down gracefully...")

# ─────────────────────────────────────────────────────────
# App Definition
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    user_id: str = Field(..., description="Unique ID for the user (for history)")
    question: str = Field(..., min_length=1, max_length=2000)

class AskResponse(BaseModel):
    user_id: str
    question: str
    answer: str
    model: str
    timestamp: str

# ─────────────────────────────────────────────────────────
# Middleware for Request Logging
# ─────────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    
    logger.info(
        f"Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": duration
        }
    )
    return response

# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.get("/health", tags=["Ops"])
def health():
    """Liveness probe."""
    return {"status": "ok", "uptime": round(time.time() - START_TIME, 1)}

@app.get("/ready", tags=["Ops"])
def ready():
    """Readiness probe."""
    if not _is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Check Redis again for readiness
    try:
        redis_client.ping()
    except Exception as e:
        logger.error(f"Readiness check failed: Redis ping failed. Error: {e}")
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {e}")
        
    return {"status": "ready"}

@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Primary endpoint for AI interaction.
    Now fault-tolerant: works even if Redis is down.
    """
    # 1. Rate Limiting & 2. Cost Guard (Wrapped in try-except in their modules)
    try:
        await check_rate_limit(api_key)
        await check_budget(api_key)
    except Exception as e:
        logger.warning(f"Protective checks bypassed due to Redis issue: {e}")
    
    # 3. Stateless History — Get from Redis
    history = []
    history_key = f"history:{body.user_id}"
    try:
        history_json = redis_client.get(history_key)
        if history_json:
            history = json.loads(history_json)
    except Exception as e:
        logger.warning(f"Failed to retrieve history from Redis: {e}")
    
    # 4. Process Question (Gemini LLM)
    answer = gemini_service.ask(body.question, history=history)
    
    # 5. Update History in Redis
    try:
        history.append({"q": body.question, "a": answer})
        history = history[-5:]
        redis_client.setex(history_key, 3600, json.dumps(history))
    except Exception as e:
        logger.warning(f"Failed to save history to Redis: {e}")
    
    return AskResponse(
        user_id=body.user_id,
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# ─────────────────────────────────────────────────────────
# Graceful Shutdown Handler
# ─────────────────────────────────────────────────────────
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}. Preparing to exit...")
    # Add any specific teardown logic here (close db connections, etc.)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
