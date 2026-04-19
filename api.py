from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel
import joblib
import logging
import urllib.parse
import re

# Cấu hình log để dễ theo dõi
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="AI Security Gateway API", description="API kiểm duyệt SQL Injection")

# Tải mô hình và vectorizer vào bộ nhớ
logger.info("Đang tải mô hình Machine Learning...")
try:
    model = joblib.load('models/rf_sqli_model.pkl')
    vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    logger.info("Tải mô hình thành công!")
except Exception as e:
    logger.error(f"Lỗi tải mô hình: {e}")
    raise RuntimeError("Không tìm thấy file mô hình. Vui lòng chạy train_model.py trước.")

def normalize_payload(payload: str) -> str:
    """
    Module Chuẩn hóa dữ liệu (Data Normalization)
    Giúp chống lại các kỹ thuật làm rối mã (Obfuscation)
    """
    if not payload:
        return ""
    
    # 1. Giải mã URL (Ví dụ: %27 biến thành ')
    text = urllib.parse.unquote(payload)
    
    # 2. Xóa các chú thích SQL kiểu /**/
    text = re.sub(r'/\*.*?\*/', '', text)
    
    # 3. Nén khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    # 4. Chuyển về chữ thường
    text = text.lower().strip()
    
    return text

# Định nghĩa cấu trúc dữ liệu đầu vào
class QueryRequest(BaseModel):
    query: str

@app.post("/analyze")
async def analyze_query(request: QueryRequest):
    try:
        raw_text = request.query
        
        # Đi qua module chuẩn hóa trước khi vào AI
        normalized_text = normalize_payload(raw_text)
        
        vectorized_text = vectorizer.transform([normalized_text])
        prediction = model.predict(vectorized_text)[0]
        
        probabilities = model.predict_proba(vectorized_text)[0]
        confidence = probabilities[prediction]

        is_sqli = bool(prediction == 1)
        
        if is_sqli:
            logger.warning(f"[CẢNH BÁO] Phát hiện SQLi (Tỷ lệ: {confidence:.2f}): {raw_text}")
        else:
            logger.info(f"[AN TOÀN] Truy vấn bình thường: {raw_text}")

        return {
            "query": request.query,
            "normalized_query": normalized_text,
            "is_sqli": is_sqli,
            "confidence": round(confidence, 4)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verify")
async def verify_gateway(x_original_uri: str = Header(None)):
    """
    Endpoint dành riêng cho Nginx Gateway.
    """
    if not x_original_uri:
        return Response(status_code=200)
    
    # --- THÊM LỚP WHITELIST Ở ĐÂY ---
    # Các URL an toàn tuyệt đối không cần qua AI kiểm duyệt
    safe_paths = ["/", "/favicon.ico"]
    
    # Tách lấy phần đường dẫn (bỏ phần tham số phía sau dấu ? nếu có để so sánh)
    path_only = x_original_uri.split('?')[0]
    
    # Nếu đường dẫn không có tham số (chỉ là /) hoặc là favicon, cho qua luôn!
    if x_original_uri in safe_paths:
        logger.info(f"[WHITELIST] Bỏ qua kiểm tra AI cho đường dẫn an toàn: {x_original_uri}")
        return Response(status_code=200)
    # ---------------------------------
    
    # 1. Tiền xử lý: Đưa URL qua module chuẩn hóa dữ liệu
    normalized_uri = normalize_payload(x_original_uri)
    
    # 2. Đưa vào mô hình AI kiểm tra
    vectorized_text = vectorizer.transform([normalized_uri])
    prediction = model.predict(vectorized_text)[0]
    
    if prediction == 1:
        logger.warning(f"[CHẶN] Phát hiện SQLi trên URL (sau chuẩn hóa): {normalized_uri}")
        raise HTTPException(status_code=403, detail="SQL Injection Detected")
    
    logger.info(f"[HỢP LỆ] URL an toàn: {normalized_uri}")
    return Response(status_code=200)