import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

# 1. Đọc dữ liệu
df = pd.read_csv("data/Iris.csv")

# 2. Chọn dữ liệu đầu vào và nhãn
X = df[
    [
        "SepalLengthCm",
        "SepalWidthCm",
        "PetalLengthCm",
        "PetalWidthCm"
    ]
]

y = df["Species"]

# 3. Chia dữ liệu train và test
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 4. Tạo mô hình SVM
model = SVC(kernel="rbf")

# 5. Huấn luyện
model.fit(X_train, y_train)

# 6. Dự đoán
y_pred = model.predict(X_test)

# 7. Đánh giá
accuracy = accuracy_score(y_test, y_pred)

print("Độ chính xác:", accuracy)
print("\nBáo cáo phân loại:")
print(classification_report(y_test, y_pred))