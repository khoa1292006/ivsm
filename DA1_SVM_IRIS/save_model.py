import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

# Đọc dữ liệu
df = pd.read_csv("data/Iris.csv")

# Dữ liệu đầu vào
X = df[
    [
        "SepalLengthCm",
        "SepalWidthCm",
        "PetalLengthCm",
        "PetalWidthCm"
    ]
]

# Nhãn
y = df["Species"]

# Chia dữ liệu
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Tạo và huấn luyện SVM
model = SVC(kernel="rbf")
model.fit(X_train, y_train)

# Lưu mô hình
joblib.dump(model, "svm_iris.pkl")

print("Đã lưu mô hình thành công: svm_iris.pkl")