# Production AI Agent

A production-ready AI agent built with FastAPI, Docker, and Redis.

## Features
- ✅ **API Security**: Authentication via `X-API-Key` header.
- ✅ **Rate Limiting**: Redis-based, 10 requests per minute per user.
- ✅ **Cost Guard**: Redis-based, $10 per month budget per user.
- ✅ **Stateless Design**: Conversation history and limits stored in Redis for horizontal scaling.
- ✅ **Structured Logging**: JSON logs for easy observability.
- ✅ **Production-Ready**: Multi-stage Docker build, health checks, and graceful shutdown.

## Quick Start (Local)

1. **Clone the project** and navigate to the directory.
2. **Setup environment**:
   ```bash
   cp .env.example .env
   ```
3. **Run with Docker Compose**:
   ```bash
   docker compose up --build
   ```

## API Documentation
- **Health Check**: `GET /health`
- **Readiness Check**: `GET /ready`
- **Ask Agent**: `POST /ask`
  - Header: `X-API-Key: your-secret-key-123`
  - Body: `{"user_id": "user1", "question": "What is Docker?"}`

## Testing

```bash
# Test Health
curl http://localhost:8000/health

# Test Ask (Requires Key)
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "question": "Hello Agent"}'
```

## Deployment
This project is configured for **Railway** via `railway.toml`. Simply connect your GitHub repository and set the environment variables in the Railway dashboard.
