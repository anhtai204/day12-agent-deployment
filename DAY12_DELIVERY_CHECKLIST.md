# Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Nguyễn Anh Tài  
> **Student ID:** 2A202600388  
> **Date:** 17/04/2026

---

## Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

`````markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. Hardcode secrets (API_KEY, DB_URL)
2. Không có rate limiting
3. Debug mode bật → lộ log nhạy cảm
4. Không có health check
5. Port hardcode, không đọc từ ENV
   ...

### Exercise 1.2: Chạy basic version

Ứng dụng chạy OK (200) nhưng **chưa production-ready**:

- Lộ API key
- Không authentication
- Không rate limit
- Không monitoring / health checks

### Exercise 1.3: Comparison table

| Feature      | Development | Production            | Why Important     |
| ------------ | ----------- | --------------------- | ----------------- |
| Config       | Hardcode    | Environment variables | Tránh lộ secrets  |
| Health check | Không có    | `/health` endpoint    | Monitoring        |
| Logging      | print()     | Structured logging    | Tránh lộ dữ liệu  |
| Shutdown     | Kill ngay   | Graceful shutdown     | Tránh mất request |

...

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Base image: python:3.11

- Thay vì build lại từ đầu, sử dụng các bộ khung mà các nhà phát triển đã tạo.

2. Working directory: /app

- Tất cả sẽ chạy trong folder /app

3.  Copy `requirements.txt` trước để tránh reinstall mỗi lần build.

### Exercise 2.2: Build và run

- Image size my-agent:develop: 424MB
  IMAGE ID DISK USAGE CONTENT SIZE  
  my-agent:develop 9462f2b1e75b 1.66GB 424MB

### Exercise 2.3: Image size comparison

- Develop: [424] MB
- Production: [56.6MB] MB
- Difference: [86.65]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- URL: https://railway-init-project-production.up.railway.app
- Screenshot:
  {"message":"AI Agent running on Railway!","docs":"/docs","health":"/health"}

## Part 4: API Security

### Exercise 4.1-4.3: Test results

- API key được lấy trong file .env
- Không có key:
  {
  "detail": "Missing API key. Include header: X-API-Key: <your-key>"
  }
- Có key:
  {
  "question": "hello",
  "answer": "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."
  }

### Exercise 4.4: Cost guard implementation

- Dùng Redis để lưu chi phí theo từng user theo tháng với key budget:{user_id}:{YYYY-MM}. Mỗi request sẽ lấy tổng chi phí hiện tại, cộng thêm chi phí ước tính rồi so sánh với ngân sách $10/tháng. Nếu vượt thì chặn, nếu không thì cập nhật lại Redis. Sang tháng mới tự reset nhờ key mới.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

> 5.1 Health checks:

- Đã triển khai `/health` trả về JSON `{"status": "ok", "uptime": X}` để platform theo dõi trạng thái sống của container.
- Đã triển khai `/ready` thực hiện `redis_client.ping()` để đảm bảo Agent chỉ nhận traffic khi đã kết nối được cơ sở dữ liệu.

> 5.2 Graceful shutdown:

- Sử dụng thư viện `signal` để bắt `SIGTERM`. Khi nhận tín hiệu, Agent sẽ log trạng thái shutdown và hoàn thành các task xử lý LLM đang chạy trước khi thoát process.

> 5.3 Stateless design:

- Loại bỏ biến `history` trong bộ nhớ. Toàn bộ lịch sử hội thoại được lưu/truy vấn từ Redis bằng `user_id`, cho phép scale ngang (Horizontal Scaling) mà không mất dữ liệu.

> 5.4 Load balancing:

- Ứng dụng được Docker hóa hoàn toàn, sẵn sàng chạy sau Nginx hoặc Load Balancer Layer 7 của Railway để phân phối tải.

> 5.5 Verification:

- Đã kiểm tra qua log Railway: Khi ứng dụng restart hoặc redeploy (trigger SIGTERM), các session cũ vẫn tiếp tục được nhận diện nhờ dữ liệu được persist trong Redis.

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

your-repo/
├── app/
│ ├── main.py # Main application
│ ├── config.py # Configuration
│ ├── auth.py # Authentication
│ ├── rate_limiter.py # Rate limiting
│ └── cost_guard.py # Cost protection
├── utils/
│ └── mock_llm.py # Mock LLM (provided)
├── Dockerfile # Multi-stage build
├── docker-compose.yml # Full stack
├── requirements.txt # Dependencies
├── .env.example # Environment template
├── .dockerignore # Docker ignore
├── railway.toml # Railway config (or render.yaml)
└── README.md # Setup instructions

**Requirements:**

- All code runs without errors
- Multi-stage Dockerfile (image < 500 MB)
- API key authentication
- Rate limiting (10 req/min)
- Cost guard ($10/month)
- Health + readiness checks
- Graceful shutdown
- Stateless design (Redis)
- No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

````markdown
# Deployment Information

## Public URL

> https://railway-init-project-production.up.railway.app/

## Platform

> Railway

## Test Commands

### Health Check

```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```
````
`````

````

### API Test (with authentication)

```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

> ..\my-production-agent>curl https://railway-init-project-production.up.railway.app/health
{"status":"ok","uptime":21.2}

> ..\my-production-agent>curl https://railway-init-project-production.up.railway.app/ready
{"status":"ready"}

> ..\my-production-agent>curl -X POST "https://railway-init-project-production.up.railway.app/ask" -H "X-API-Key: 22042004" -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"question\":\"Docker là gì?\"}"
{"user_id":"test_user","question":"Docker là gì?","answer":"Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!","model":"gemini-1.5-flash","timestamp":"2026-04-17T14:41:02.096907+00:00"}

> ..\my-production-agent>curl -X POST "https://railway-init-project-production.up.railway.app/ask" -H "X-API-Key: 22042004" -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"question\":\"Làm sao để deploy app?\"}"
{"user_id":"test_user","question":"Làm sao để deploy app?","answer":"Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được.","model":"gemini-1.5-flash","timestamp":"2026-04-17T14:41:07.312892+00:00"}



## Environment Variables Set

- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots

- [Deployment dashboard](screenshots/dashboard.png) [screenshots\dashboard.png]
- [Service running](screenshots/running.png) [screenshots\running.png]
- [Test results](screenshots/test.png) [screenshots\test.png]

````

## Pre-Submission Checklist

- [x] Repository is public (or instructor has access)
- [x] `MISSION_ANSWERS.md` completed with all exercises
- [x] `DEPLOYMENT.md` has working public URL
- [x] All source code in `app/` directory
- [x] `README.md` has clear setup instructions
- [x] No `.env` file committed (only `.env.example`)
- [x] No hardcoded secrets in code
- [x] Public URL is accessible and working
- [x] Screenshots included in `screenshots/` folder
- [x] Repository has clear commit history

---

## Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}';
done
# Should eventually return 429


> ..\my-production-agent>curl https://railway-init-project-production.up.railway.app/health
{"status":"ok","uptime":21.2}

> ..\my-production-agent>curl https://railway-init-project-production.up.railway.app/ready
{"status":"ready"}

> ..\my-production-agent>curl -X POST "https://railway-init-project-production.up.railway.app/ask" -H "X-API-Key: 22042004" -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"question\":\"Docker là gì?\"}"
{"user_id":"test_user","question":"Docker là gì?","answer":"Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!","model":"gemini-1.5-flash","timestamp":"2026-04-17T14:41:02.096907+00:00"}

> ..\my-production-agent>curl -X POST "https://railway-init-project-production.up.railway.app/ask" -H "X-API-Key: 22042004" -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\",\"question\":\"Làm sao để deploy app?\"}"
{"user_id":"test_user","question":"Làm sao để deploy app?","answer":"Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được.","model":"gemini-1.5-flash","timestamp":"2026-04-17T14:41:07.312892+00:00"}


## Validation
> python check_production_ready.py
=======================================================
  Production Readiness Check — Day 12 Lab
=======================================================

📁 Required Files
  ✅ Dockerfile exists
  ✅ docker-compose.yml exists
  ✅ .dockerignore exists
  ✅ .env.example exists
  ✅ requirements.txt exists
  ✅ railway.toml or render.yaml exists

🔒 Security
  ✅ .env in .gitignore
  ✅ No hardcoded secrets in code

🌐 API Endpoints (code check)
  ✅ /health endpoint defined
  ✅ /ready endpoint defined
  ✅ Authentication implemented
  ✅ Rate limiting implemented
  ✅ Graceful shutdown (SIGTERM)
  ✅ Structured logging (JSON)

🐳 Docker
  ✅ Multi-stage build
  ✅ Non-root user
  ✅ HEALTHCHECK instruction
  ✅ Slim base image
  ✅ .dockerignore covers .env
  ✅ .dockerignore covers __pycache__

=======================================================
  Result: 20/20 checks passed (100%)
  🎉 PRODUCTION READY! Deploy nào!
=======================================================

---

## Submission

**Submit your GitHub repository URL:**

```

https://github.com/anhtai204/day12-agent-deployment.git

```

**Deadline:** 17/4/2026

---

## Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

## Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
```
