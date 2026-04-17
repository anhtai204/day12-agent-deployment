## 1. Cấu trúc Hệ thống (Architecture)

Hệ thống được thiết kế theo mô hình **Stateless AI Agent**, bao gồm:

- **FastAPI (Backend)**: Xử lý logic nghiệp vụ, quản lý hội thoại và kết nối LLM.
- **Redis (Database)**: Lưu trữ lịch sử hội thoại (stateless) và thực hiện giới hạn (Rate Limit/Cost Guard).
- **Deployment**: Chạy trên Docker container trực tiếp

## 2. Cấu hình Biến môi trường (Environment Variables)

Để Agent hoạt động ổn định, bạn cần thiết lập các biến sau trên Railway (Tab Variables):

| Biến             | Ý nghĩa                  | Ví dụ                                     |
| :--------------- | :----------------------- | :---------------------------------------- |
| `AGENT_API_KEY`  | Key bảo mật để gọi API   | `22042004`                                |
| `REDIS_URL`      | URL kết nối Redis nội bộ | `redis://default:pass@host.internal:6379` |
| `GEMINI_API_KEY` | Key từ Google AI Studio  | `AIzaSy...` (Tùy chọn)                    |
| `ENVIRONMENT`    | Môi trường chạy          | `production`                              |

## 3. Quy trình Triển khai (Railway CLI)

Dự án này được tối ưu để deploy nhanh chóng qua CLI mà không cần cài đặt GitHub:

1. **Liên kết Project**:
   ```bash
   railway link
   ```
2. **Thiết lập biến (nếu chưa có)**:
   ```bash
   railway variables set AGENT_API_KEY=22042004
   ```
3. **Triển khai**:
   ```bash
   railway up
   ```

## 4. Test Plan

Sau khi deploy thành công, hãy thực hiện 3 bước kiểm tra sau:

### Bước 1: Kiểm tra Health Check

Xác nhận server Agent đã online.

```bash
curl https://railway-init-project-production.up.railway.app/health
> Kết quả: {"status":"ok","uptime":21.2}
```

### Bước 2: Kiểm tra "Sẵn sàng" (Readiness Check)

Xác nhận Agent đã kết nối thành công với Redis Database.

```bash
curl https://railway-init-project-production.up.railway.app/ready
> Kết quả: {"status":"ready"}
```

### Bước 3: Kiểm tra Logic Agent (AI Ask)

Gửi câu hỏi và kiểm tra tính năng bảo mật + lưu lịch sử.

```bash
curl -X POST https://railway-init-project-production.up.railway.app/ask \
  -H "X-API-Key: 22042004" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "sv_01",
    "question": "Docker là gì??"
  }'

> Kết quả:
{"user_id":"test_user","question":"Docker là gì?","answer":"Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!","model":"gemini-1.5-flash","timestamp":"2026-04-17T14:41:02.096907+00:00"}
```

## 5. Xử lý sự cố (Troubleshooting)

- **Lỗi 503 (Redis unavailable)**: Kiểm tra lại `REDIS_URL`. Hãy đảm bảo dùng URL nội bộ (`.internal`).
- **Lỗi 401/403 (Unauthorized)**: Kiểm tra xem `X-API-Key` gửi đi có khớp với `AGENT_API_KEY` trên Railway không.
- **Lỗi Protocol (HTTP 400)**: Bạn đang dùng nhầm Port hoặc URL Proxy công cộng của Redis thay vì URL chuẩn.

---
