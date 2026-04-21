from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel
import joblib
import logging
import urllib.parse
import re
import redis
import uuid

# Cấu hình log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Security Gateway API", description="API kiểm duyệt SQL Injection")

# --- KHỞI TẠO REDIS ---
redis_client = None
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True, socket_connect_timeout=5)
    redis_client.ping()
    logger.info("✅ Kết nối Redis Cache thành công!")
except Exception as e:
    logger.warning(f"⚠️ Lỗi kết nối Redis: {e}")

# --- TẢI MÔ HÌNH ---
try:
    model = joblib.load('models/rf_sqli_model.pkl')
    vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    logger.info("✅ Tải mô hình thành công!")
except Exception as e:
    logger.error(f"❌ Lỗi tải mô hình: {e}")

def normalize_payload(payload: str) -> str:
    if not payload: return ""
    text = urllib.parse.unquote(payload)
    text = re.sub(r'/\*.*?\*/', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

class QueryRequest(BaseModel):
    query: str

# API Phân tích cũ (Giữ nguyên để không mất chức năng)
@app.post("/analyze")
async def analyze_query(request: QueryRequest):
    try:
        normalized_text = normalize_payload(request.query)
        vectorized_text = vectorizer.transform([normalized_text])
        prediction = model.predict(vectorized_text)[0]
        confidence = model.predict_proba(vectorized_text)[0][prediction]
        return {"query": request.query, "is_sqli": bool(prediction == 1), "confidence": round(confidence, 4)}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# API GIẢI CAPTCHA (Cấp thẻ bài dùng 1 lần)
class CaptchaSolveRequest(BaseModel):
    ip_address: str

@app.post("/solve-captcha")
async def solve_captcha(request: CaptchaSolveRequest):
    if not redis_client: raise HTTPException(status_code=500, detail="Redis không hoạt động")
    clearance_token = f"human_{uuid.uuid4().hex[:8]}"
    # Thẻ bài chỉ có tác dụng trong 5 phút để user kịp F5 trang
    redis_client.setex(f"captcha_clearance_{request.ip_address}", 300, clearance_token)
    logger.info(f"🎉 [CAPTCHA SOLVED] IP {request.ip_address} đã xác minh. Thẻ bài: {clearance_token}")
    return {"message": "Xác thực thành công!", "token": clearance_token}

# =========================================================
# BỘ LỌC CỐT LÕI (KIẾN TRÚC 4 LỚP NÂNG CAO)
# =========================================================
@app.get("/verify")
async def verify_gateway(x_original_uri: str = Header(None), x_real_ip: str = Header(None)):
    if not x_original_uri: return Response(status_code=200)
        
    # LỚP 1: THREAT INTELLIGENCE (CHẶN IP ĐEN)
    if x_real_ip:
        GLOBAL_BLACKLIST = ["203.0.113.42", "198.51.100.77", "104.28.10.50"]
        if x_real_ip in GLOBAL_BLACKLIST:
            logger.error(f"🚨 [THREAT INTEL] Chặn IP đen: {x_real_ip}")
            raise HTTPException(status_code=403, detail="Blacklisted IP")

    # LỚP 2: WHITELIST
    if x_original_uri in ["/", "/favicon.ico"]:
        return Response(status_code=200)
    
    normalized_uri = normalize_payload(x_original_uri)

    # LỚP 3: REDIS CACHE (CHỈ CACHE NHỮNG GÌ CHẮC CHẮN AN TOÀN)
    if redis_client:
        cached = redis_client.get(normalized_uri)
        if cached == "0": return Response(status_code=200)

    # LỚP 4: AI MODEL (KIỂM TRA NGHIÊM NGẶT)
    try:
        vectorized_text = vectorizer.transform([normalized_uri])
        confidence = model.predict_proba(vectorized_text)[0][1] 

        # MỨC 1: ĐỘC HẠI (>= 80%) -> Chặn vĩnh viễn
        if confidence >= 0.80:
            logger.warning(f"🤖 [AI: ĐỘC HẠI] {confidence:.2f} -> KHÓA: {normalized_uri}")
            if redis_client: redis_client.setex(normalized_uri, 86400, "1")
            raise HTTPException(status_code=403, detail="SQL Injection Detected")
            
        # MỨC 2: NGHI NGỜ (>= 20%) -> BẮT GIẢI CAPTCHA MỖI LẦN
        elif confidence >= 0.20:
            # Kiểm tra xem có thẻ bài vừa mới giải không?
            if redis_client and x_real_ip:
                has_token = redis_client.get(f"captcha_clearance_{x_real_ip}")
                if has_token:
                    logger.info(f"🛂 [VIP PASS] IP {x_real_ip} dùng thẻ bài qua cửa. Xóa thẻ ngay!")
                    redis_client.delete(f"captcha_clearance_{x_real_ip}") # XÓA THẺ: Lần sau lại bắt giải tiếp
                    return Response(status_code=200)

            logger.warning(f"🤔 [AI: NGHI NGỜ] {confidence:.2f} -> BẬT CAPTCHA: {normalized_uri}")
            raise HTTPException(status_code=401, detail="CAPTCHA Required")
            
        # MỨC 3: AN TOÀN (< 20%) -> Cho qua
        else:
            logger.info(f"✅ [AI: AN TOÀN] {confidence:.2f}: {normalized_uri}")
            if redis_client: redis_client.setex(normalized_uri, 3600, "0")
            return Response(status_code=200)
        
    except HTTPException: raise 
    except Exception as e:
        logger.error(f"❌ Lỗi: {e}")
        return Response(status_code=200)