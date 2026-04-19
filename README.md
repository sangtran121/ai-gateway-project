<div align="center">

# 🛡️ AI-Assisted API Gateway
### Defense-in-Depth · SQL Injection Detection · Machine Learning

[![CI Pipeline](https://github.com/sangtran121/ai-gateway-project/actions/workflows/ci-pipeline.yml/badge.svg)](https://github.com/sangtran121/ai-gateway-project/actions/workflows/ci-pipeline.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Gateway-009639?logo=nginx&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Random%20Forest-F7931E?logo=scikitlearn&logoColor=white)

<br/>

Một hệ thống **Reverse Proxy thực nghiệm** tích hợp Machine Learning, phân loại và đánh chặn tấn công **SQL Injection** tại tầng ứng dụng (Layer 7) theo nguyên tắc **Phòng thủ chiều sâu (Defense-in-Depth)**.

> ⚠️ **Lưu ý:** Mô hình AI đóng vai trò là lớp lọc *tăng cường*, hoạt động song song với các biện pháp bảo mật truyền thống — không thay thế hoàn toàn các giải pháp WAF thương mại.

</div>

---

## 📐 Kiến trúc Hệ thống

Mọi request đều đi qua **4 lớp bảo vệ** trước khi được định tuyến tới Backend:

```
Client Request
      │
      ▼
┌─────────────────────────────┐
│  Layer 1 · Rate Limiting    │  ← Chống DoS & Brute-force
├─────────────────────────────┤
│  Layer 2 · Static WAF Rules │  ← Chặn XSS, Path Traversal
├─────────────────────────────┤
│  Layer 3 · Normalization    │  ← URL decode, strip /**/, trim
├─────────────────────────────┤
│  Layer 4 · ML Model         │  ← Random Forest + N-gram
└─────────────────────────────┘
      │
      ▼
   Backend
```

| Lớp | Vai trò | Kỹ thuật |
|-----|---------|----------|
| Rate Limiting | Ngăn DoS, brute-force quy mô nhỏ | Nginx limit_req |
| Static WAF | Chặn payload XSS & Path Traversal lộ liễu | Nginx regex rules |
| Normalization | Chống obfuscation cơ bản | URL decode · xóa `/**/` · nén whitespace |
| ML Model | Nhận diện SQLi phức tạp còn sót lại | Random Forest + N-gram (Scikit-learn) |

---

## 🛠️ Công nghệ sử dụng

| Nhóm | Công cụ |
|------|---------|
| **Backend & API** | Python · FastAPI · Uvicorn |
| **Machine Learning** | Scikit-learn · Pandas · Kaggle dataset |
| **Infrastructure** | Docker · Docker Compose · Nginx |
| **DevSecOps** | GitHub Actions CI/CD |

---

## ⚙️ Cài đặt & Khởi chạy

### Yêu cầu

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (bật WSL 2 nếu dùng Windows)

### Các bước

**1. Clone repository**
```bash
git clone https://github.com/sangtran121/ai-gateway-project.git
cd ai-gateway-project
```

**2. Khởi động hệ thống**
```bash
docker compose up -d --build
```
> Lần đầu chạy có thể mất 1–3 phút. Sau khi hoàn tất, hệ thống lắng nghe tại `http://localhost:80`.

**3. Kiểm tra trạng thái container**
```bash
docker compose ps
```
Tất cả các container phải ở trạng thái `Up`.

---

## 🎯 Kiểm thử

### Kịch bản 1 — Truy cập hợp lệ ✅

```
GET http://localhost/?product=shoes
```

**Kết quả:** Gateway cho phép đi qua. Trình duyệt hiển thị trang thông tin Backend (Server address, Server name).

---

### Kịch bản 2 — SQL Injection cơ bản 🚫

```
GET http://localhost/?username=admin' OR 1=1--
```

**Kết quả:** `403 Forbidden` — Request bị chặn ngay tại Gateway.

---

### Kịch bản 3 — Obfuscation Attack 🚫

```
GET http://localhost/?username=admin%27/**/OR/**/1=1--
```

**Kết quả:** `403 Forbidden` — Lớp Normalization làm sạch payload trước khi ML model nhận diện.

---

### Xem log phân tích của AI

```bash
docker compose logs -f security_api
```

> Nhấn `Ctrl + C` để thoát.

---

## 🛑 Dừng hệ thống

```bash
docker compose down
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
