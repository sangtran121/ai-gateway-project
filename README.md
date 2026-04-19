# 🛡️ AI-Assisted API Gateway (Defense-in-Depth)

[![DevSecOps AI Gateway Pipeline](https://github.com/sangtran121/ai-gateway-project/actions/workflows/ci-pipeline.yml/badge.svg)](https://github.com/sangtran121/ai-gateway-project/actions/workflows/ci-pipeline.yml)

Đây là một dự án thực nghiệm nhằm xây dựng hệ thống Reverse Proxy tích hợp Machine Learning. Mục tiêu của dự án là phân loại và đánh chặn các cuộc tấn công SQL Injection ở tầng ứng dụng (Layer 7) bằng cách áp dụng nguyên tắc Phòng thủ chiều sâu (Defense-in-Depth). 

*Lưu ý: Mô hình AI đóng vai trò như một lớp lọc tăng cường, hoạt động song song với các biện pháp bảo mật truyền thống, không thay thế hoàn toàn các giải pháp WAF thương mại.*

## 🚀 Kiến trúc Hệ thống

Hệ thống sử dụng Nginx làm API Gateway, xử lý lưu lượng qua 4 lớp khiên bảo mật trước khi định tuyến vào Backend:
1. **Rate Limiting:** Chống lại các cuộc tấn công DoS và Brute-force quy mô nhỏ.
2. **Static WAF Rules:** Chặn các payload XSS và Path Traversal lộ liễu.
3. **Data Normalization:** Tiền xử lý dữ liệu (URL decoding, xóa chú thích `/**/`, nén khoảng trắng) để chống lại các kỹ thuật Obfuscation (làm rối mã) cơ bản.
4. **Machine Learning Model:** Sử dụng thuật toán Random Forest phân tích N-gram để nhận diện các truy vấn SQL Injection phức tạp đã vượt qua các lớp trên.

## 🛠️ Công nghệ sử dụng
* **Backend & API:** Python, FastAPI, Uvicorn.
* **Machine Learning:** Scikit-learn, Pandas (Huấn luyện với tập dữ liệu từ Kaggle).
* **Infrastructure:** Docker, Docker Compose, Nginx.
* **DevSecOps:** GitHub Actions (Automated Testing CI/CD Pipeline).

---

## ⚙️ Hướng dẫn Cài đặt & Khởi chạy

Để chạy dự án này trên máy cá nhân, bạn chỉ cần thực hiện theo các bước dưới đây.

### 1. Yêu cầu hệ thống (Prerequisites)
Đảm bảo máy tính của bạn đã cài đặt sẵn:
* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/) và Docker Compose (Bật tính năng WSL 2 nếu bạn dùng Windows).

### 2. Tải mã nguồn
Mở Terminal/Command Prompt và chạy lệnh:
```bash
git clone [https://github.com/sangtran121/ai-gateway-project.git](https://github.com/sangtran121/ai-gateway-project.git)
cd ai-gateway-project
