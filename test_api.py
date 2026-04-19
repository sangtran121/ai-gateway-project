import requests
import time
import sys

# URL của Gateway đang chạy local
BASE_URL = "http://localhost:80"

print("Đang chờ hệ thống Gateway khởi động (10 giây)...")
time.sleep(10) # Đợi các container Docker chạy lên hoàn toàn

def test_safe_request():
    print("[-] Đang test request hợp lệ...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"LỖI: Request an toàn bị chặn (Mã {response.status_code})"
    print("   -> [PASS] Request an toàn đi qua thành công.")

def test_sqli_request():
    print("[-] Đang test đòn tấn công SQL Injection...")
    # Truyền payload chứa /**/ để test luôn module Chuẩn hóa dữ liệu
    payload = "admin'/**/or/**/1=1--"
    response = requests.get(f"{BASE_URL}/?username={payload}")
    assert response.status_code == 403, f"LỖI NGUY HIỂM: Payload SQLi lọt qua Gateway! (Mã {response.status_code})"
    print("   -> [PASS] Đã chặn đứng SQLi thành công (Mã 403).")

if __name__ == "__main__":
    try:
        test_safe_request()
        test_sqli_request()
        print("\n[TẤT CẢ KIỂM THỬ THÀNH CÔNG] Hệ thống Gateway an toàn tuyệt đối! 🚀")
        sys.exit(0) # Báo cho GitHub Actions biết là test pass
    except AssertionError as e:
        print(f"\n[KIỂM THỬ THẤT BẠI] {e} ❌")
        sys.exit(1) # Báo cho GitHub Actions biết là test fail để hủy quy trình