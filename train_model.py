import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# 1. Tải dữ liệu
data_path = 'data/Modified_SQL_Dataset.csv'
print(f"Đang đọc dữ liệu từ: {data_path}...")
df = pd.read_csv(data_path)

# In ra tên các cột để kiểm tra (Thường Kaggle dataset sẽ có cột 'Query' và 'Label')
print("Các cột trong dataset:", df.columns.tolist())

# Xử lý dữ liệu rỗng (nếu có) để tránh lỗi
# Giả sử cột chứa text là 'Query' và cột nhãn là 'Label'. 
# LƯU Ý: Nếu tên cột của bạn khác, hãy sửa lại hai biến dưới đây cho đúng.
text_col = 'Query' 
label_col = 'Label'

df[text_col] = df[text_col].fillna('')
df[text_col] = df[text_col].astype(str).str.lower() # Chuyển hết về chữ thường

X_raw = df[text_col]
y = df[label_col]

# 2. Trích xuất đặc trưng (Chuyển chữ thành số)
# Sử dụng TF-IDF với ngram_range=(1, 3) để bắt được các cụm ký tự như ' OR 1=1
print("Đang vector hóa dữ liệu...")
vectorizer = TfidfVectorizer(min_df=2, analyzer='char_wb', ngram_range=(1, 3))
X = vectorizer.fit_transform(X_raw)

# 3. Chia tập dữ liệu (80% huấn luyện, 20% kiểm tra)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Huấn luyện mô hình Random Forest
print("Đang huấn luyện mô hình Random Forest (có thể mất chút thời gian)...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 5. Đánh giá mô hình
print("Đang đánh giá mô hình trên tập Test...")
y_pred = model.predict(X_test)
print(f"\nĐộ chính xác (Accuracy): {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print("Báo cáo chi tiết (Classification Report):")
print(classification_report(y_test, y_pred))

# 6. Đóng gói và lưu mô hình & vectorizer
# Đây là bước quan trọng để tái sử dụng cho API Gateway
print("Đang lưu mô hình để sử dụng cho API...")
os.makedirs('models', exist_ok=True) # Tạo thư mục 'models' nếu chưa có

joblib.dump(model, 'models/rf_sqli_model.pkl')
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')

print("Hoàn tất! Đã lưu mô hình tại thư mục 'models/'.")