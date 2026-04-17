# Hướng dẫn Triển khai & Cài đặt AI Agent (Production)

Tài liệu này hướng dẫn cách cấu hình, triển khai và kiểm tra AI Agent trên môi trường Cloud (Railway) với cấu trúc tinh gọn nhất.

## 1. Cấu trúc Hệ thống (Architecture)

Hệ thống được thiết kế theo mô hình **Stateless AI Agent**, bao gồm:
- **FastAPI (Backend)**: Xử lý logic nghiệp vụ, quản lý hội thoại và kết nối LLM.
- **Redis (Database)**: Lưu trữ lịch sử hội thoại (stateless) và thực hiện giới hạn (Rate Limit/Cost Guard).
- **Deployment**: Chạy trên Docker container trực tiếp, không sử dụng Nginx để tối ưu độ phức tạp.

## 2. Cấu hình Biến môi trường (Environment Variables)

Để Agent hoạt động ổn định, bạn cần thiết lập các biến sau trên Railway (Tab Variables):

| Biến | Ý nghĩa | Ví dụ |
| :--- | :--- | :--- |
| `AGENT_API_KEY` | Key bảo mật để gọi API | `22042004` |
| `REDIS_URL` | URL kết nối Redis nội bộ | `redis://default:pass@host.internal:6379` |
| `GEMINI_API_KEY` | Key từ Google AI Studio | `AIzaSy...` (Tùy chọn) |
| `ENVIRONMENT` | Môi trường chạy | `production` |

> [!TIP]
> **Ưu tiên kết nối nội bộ**: Hãy luôn sử dụng **Internal Redis URL** từ tab Connect của dịch vụ Redis trên Railway thay vì Public Proxy để đảm bảo tốc độ và không bị ngắt kết nối.

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

## 4. Hướng dẫn Thử nghiệm (Test Plan)

Sau khi deploy thành công, hãy thực hiện 3 bước kiểm tra sau:

### Bước 1: Kiểm tra "Sống sót" (Health Check)
Xác nhận server Agent đã online.
```bash
curl https://railway-init-project-production.up.railway.app/health
# Kết quả mong đợi: {"status": "ok"}
```

### Bước 2: Kiểm tra "Sẵn sàng" (Readiness Check)
Xác nhận Agent đã kết nối thành công với Redis Database.
```bash
curl https://railway-init-project-production.up.railway.app/ready
# Kết quả mong đợi: {"status": "ready"}
```

### Bước 3: Kiểm tra Logic Agent (AI Ask)
Gửi câu hỏi và kiểm tra tính năng bảo mật + lưu lịch sử.
```bash
curl -X POST https://railway-init-project-production.up.railway.app/ask \
  -H "X-API-Key: 22042004" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "sv_01",
    "question": "Kiến trúc Stateless Agent là gì?"
  }'
```


## 5. Xử lý sự cố (Troubleshooting)

- **Lỗi 503 (Redis unavailable)**: Kiểm tra lại `REDIS_URL`. Hãy đảm bảo dùng URL nội bộ (`.internal`).
- **Lỗi 401/403 (Unauthorized)**: Kiểm tra xem `X-API-Key` gửi đi có khớp với `AGENT_API_KEY` trên Railway không.
- **Lỗi Protocol (HTTP 400)**: Bạn đang dùng nhầm Port hoặc URL Proxy công cộng của Redis thay vì URL chuẩn.

---
