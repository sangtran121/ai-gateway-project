# 🛡️ AI-Driven API Gateway (Defense-in-Depth)

[![DevSecOps AI Gateway Pipeline](https://github.com/sangtran121/ai-gateway-project/actions/workflows/ci-pipeline.yml/badge.svg)](https://github.com/sangtran121/ai-gateway-project/actions/workflows/ci-pipeline.yml)

Hệ thống Reverse Proxy tích hợp Machine Learning nhằm phân loại và đánh chặn các cuộc tấn công SQL Injection ở tầng ứng dụng (Layer 7), thiết kế theo nguyên tắc Phòng thủ chiều sâu (Defense-in-Depth).

## 🚀 Kiến trúc Hệ thống
Hệ thống sử dụng Nginx làm API Gateway, xử lý lưu lượng qua 4 lớp khiên bảo mật trước khi định tuyến vào Backend:
1. **Rate Limiting:** Chống lại các cuộc tấn công DoS và Brute-force.
2. **Static WAF Rules:** Chặn các payload XSS và Path Traversal lộ liễu.
3. **Data Normalization:** Tiền xử lý (decode, xóa chú thích `/**/`, nén khoảng trắng) để chống lại kỹ thuật Obfuscation.
4. **Machine Learning Model:** Sử dụng thuật toán Random Forest phân tích N-gram để nhận diện các truy vấn SQL Injection phức tạp.

## 🛠️ Công nghệ sử dụng
* **Backend & API:** Python, FastAPI, Uvicorn.
* **Machine Learning:** Scikit-learn, Pandas (Huấn luyện với tập dữ liệu từ Kaggle).
* **Infrastructure:** Docker, Docker Compose, Nginx.
* **DevSecOps:** GitHub Actions (Automated Testing CI/CD Pipeline).
* **Network Analysis:** Wireshark.

## ⚙️ Hướng dẫn cài đặt và khởi chạy
Yêu cầu hệ thống: Docker và Docker Compose.

```bash
# Clone dự án
git clone [https://github.com/TÊN_CỦA_BẠN/ai-gateway-project.git](https://github.com/TÊN_CỦA_BẠN/ai-gateway-project.git)
cd ai-gateway-project

# Khởi chạy cụm dịch vụ
docker compose up -d --build