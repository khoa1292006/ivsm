import hashlib
import json
import os
from pathlib import Path
from typing import Dict

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. CẤU HÌNH HỆ THỐNG
# ==============================================================================
st.set_page_config(
    page_title="IRIS-SYNAPSE // Bio-Telemetry SVM",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
AUTH_DB_PATH = BASE_DIR / "users.json"
MODEL_PATH = BASE_DIR / "svm_iris.pkl"

# ==============================================================================
# 2. XÁC THỰC LƯU TRỮ VĨNH VIỄN (SHA-256)
# ==============================================================================
def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()

def get_user_database() -> Dict[str, str]:
    if not AUTH_DB_PATH.exists():
        default_db = {"lab_chief": hash_secret("bio2026"), "admin": hash_secret("admin123")}
        with open(AUTH_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4)
        return default_db
    try:
        with open(AUTH_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"admin": hash_secret("admin123")}

def save_new_user(username: str, secret: str) -> bool:
    db = get_user_database()
    if username in db:
        return False
    db[username] = hash_secret(secret)
    with open(AUTH_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)
    return True

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# ==============================================================================
# 3. CSS CYBER BIO-TECH (THEME SIÊU CẤP ĐỘNG)
# ==============================================================================
st.markdown("""
<style>
    /* Dark Sci-Fi Background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #111a2e 0%, #080c16 55%, #05070c 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Neon Glow & Glass Cards */
    .cyber-panel {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(6, 182, 212, 0.25);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6), 0 0 15px rgba(6, 182, 212, 0.1);
        margin-bottom: 20px;
    }

    .cyber-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 9999px;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-size: 0.85rem;
    }

    .badge-setosa {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid #10b981;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
    }

    .badge-versicolor {
        background: rgba(6, 182, 212, 0.15);
        color: #38bdf8;
        border: 1px solid #06b6d4;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
    }

    .badge-virginica {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid #f43f5e;
        box-shadow: 0 0 15px rgba(244, 63, 94, 0.3);
    }

    /* Hiệu ứng nút bấm Futuristic */
    .stButton>button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        height: 3.2rem !important;
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(6, 182, 212, 0.6) !important;
    }

    /* Tiêu đề Glow Gradient */
    .glitch-title {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        margin-bottom: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. MÀN HÌNH ĐĂNG NHẬP / SECURITY GATEWAY
# ==============================================================================
if not st.session_state.authenticated:
    _, center_gate, _ = st.columns([1, 1.4, 1])
    with center_gate:
        st.markdown("""
        <div style="text-align: center; margin-top: 50px; margin-bottom: 25px;">
            <div style="font-size: 3.5rem; text-shadow: 0 0 20px #06b6d4;">🧬</div>
            <h1 class="glitch-title">IRIS-SYNAPSE</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; letter-spacing: 0.08em;">PHÒNG THÍ NGHIỆM GIÁM ĐỊNH TẾ BÀO THỰC VẬT AI</p>
        </div>
        """, unsafe_allow_html=True)

        auth_tab1, auth_tab2 = st.tabs(["⚡ TRUY CẬP HỆ THỐNG", "🛰️ ĐĂNG KÝ HỒ SƠ"])
        users_db = get_user_database()

        with auth_tab1:
            with st.form("login_gateway"):
                u_in = st.text_input("Mã Chuyên Viên (User ID)", placeholder="lab_chief")
                p_in = st.text_input("Mã Khóa Bảo Mật (Password)", type="password", placeholder="••••••••")
                if st.form_submit_button("KHỞI TẠO KẾT NỐI SYNAPSE", use_container_width=True):
                    if u_in in users_db and users_db[u_in] == hash_secret(p_in):
                        st.session_state.authenticated = True
                        st.session_state.current_user = u_in
                        st.rerun()
                    else:
                        st.error("Cảnh báo: Sai mã định danh hoặc khóa truy cập.")
            st.caption("🔒 Tài khoản mẫu: `lab_chief` | Mật khẩu: `bio2026`")

        with auth_tab2:
            with st.form("reg_gateway"):
                nu = st.text_input("Tạo mã chuyên viên mới")
                npw = st.text_input("Mật khẩu", type="password")
                ncp = st.text_input("Xác nhận mật khẩu", type="password")
                if st.form_submit_button("CẤP QUYỀN MỚI VÀO DATABASE", use_container_width=True):
                    if not nu or not npw:
                        st.warning("Vui lòng điền đủ thông tin.")
                    elif nu in users_db:
                        st.error("Mã chuyên viên này đã tồn tại trên mạng lưới.")
                    elif npw != ncp:
                        st.error("Khóa mật mã xác nhận không trùng khớp.")
                    else:
                        save_new_user(nu, npw)
                        st.success(f"Đã cấp chứng chỉ cho `{nu}`! Hãy chuyển sang tab Đăng Nhập.")
    st.stop()

# ==============================================================================
# 5. ML ENGINE PIPELINE
# ==============================================================================
@st.cache_resource
def get_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass
    from sklearn.datasets import load_iris
    from sklearn.svm import SVC
    iris = load_iris()
    clf = SVC(probability=True, kernel="rbf", random_state=42)
    clf.fit(iris.data, iris.target)
    return clf

model = get_model()

# Sidebar: Trạng thái trạm điều khiển
with st.sidebar:
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
        <span style="font-size: 0.7rem; color: #06b6d4; letter-spacing: 0.15em; font-weight: bold;">OPERATOR STATUS</span>
        <h3 style="color: #f8fafc; margin: 4px 0 0 0;">👨‍🔬 {st.session_state.current_user.upper()}</h3>
        <p style="color: #10b981; font-size: 0.8rem; margin: 4px 0 0 0;">● Hệ thống Synapse kết nối trực tiếp</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📡 Thông số Trạm AI")
    st.markdown("""
    - **Cốt lõi:** Support Vector Machine
    - **Kernel Mapping:** High-dimensional RBF
    - **Tối ưu hóa:** Platt Scale Calibration
    - **Môi trường:** Python Web Telemetry
    """)
    st.divider()
    if st.button("🚪 Ngắt kết nối Terminal", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.rerun()

# ==============================================================================
# 6. WORKSPACE: PHÂN TÍCH HÌNH THÁI VÀ TRỰC QUAN HÓA
# ==============================================================================
st.markdown('<div class="glitch-title">🧬 TRUNG TÂM PHÂN TÍCH HÌNH THÁI THỰC VẬT AI</div>', unsafe_allow_html=True)
st.caption("Khảo sát vector đa chiều hình thái tế bào hoa Iris thông qua siêu phẳng phân chia SVM.")

# Quick Presets
col_p1, col_p2, col_p3 = st.columns(3)
if "p_vals" not in st.session_state:
    st.session_state.p_vals = {"sl": 5.4, "sw": 3.4, "pl": 1.5, "pw": 0.4}

if col_p1.button("🟢 Tải mẫu: Iris Setosa (Đài lớn / Cánh nhỏ)", use_container_width=True):
    st.session_state.p_vals = {"sl": 5.0, "sw": 3.5, "pl": 1.4, "pw": 0.2}
if col_p2.button("🔵 Tải mẫu: Iris Versicolor (Hình thái cân bằng)", use_container_width=True):
    st.session_state.p_vals = {"sl": 5.9, "sw": 2.7, "pl": 4.2, "pw": 1.3}
if col_p3.button("🔴 Tải mẫu: Iris Virginica (Cánh lớn cực đại)", use_container_width=True):
    st.session_state.p_vals = {"sl": 6.7, "sw": 3.1, "pl": 5.6, "pw": 2.2}

# Sliders giao diện Cyber
st.markdown('<div class="cyber-panel">', unsafe_allow_html=True)
st.markdown("#### 🎛️ Bộ cảm biến tham số sinh học (Sensors Telemetry)")

c_left, c_right = st.columns(2)
with c_left:
    sl = st.slider("🌱 Chiều dài lá đài - Sepal Length (cm)", 4.0, 8.0, float(st.session_state.p_vals["sl"]), 0.1)
    sw = st.slider("🌱 Chiều rộng lá đài - Sepal Width (cm)", 2.0, 4.5, float(st.session_state.p_vals["sw"]), 0.1)
with c_right:
    pl = st.slider("🌸 Chiều dài cánh hoa - Petal Length (cm)", 1.0, 7.0, float(st.session_state.p_vals["pl"]), 0.1)
    pw = st.slider("🌸 Chiều rộng cánh hoa - Petal Width (cm)", 0.1, 2.5, float(st.session_state.p_vals["pw"]), 0.1)
st.markdown('</div>', unsafe_allow_html=True)

# Nút kích hoạt phân tích
if st.button("⚡ KÍCH HOẠT QUÉT HÌNH THÁI & DỰ ĐOÁN SIÊU PHẲNG", use_container_width=True):
    # Vector hóa dữ liệu
    input_data = pd.DataFrame([[sl, sw, pl, pw]], columns=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"])
    try:
        pred_raw = model.predict(input_data)[0]
    except Exception:
        pred_raw = model.predict([[sl, sw, pl, pw]])[0]

    # Map nhãn
    map_dict = {
        0: "Iris-setosa", 1: "Iris-versicolor", 2: "Iris-virginica",
        "setosa": "Iris-setosa", "versicolor": "Iris-versicolor", "virginica": "Iris-virginica"
    }
    species_tag = map_dict.get(pred_raw, str(pred_raw))

    meta = {
        "Iris-setosa": {
            "name": "Iris Setosa",
            "badge": "badge-setosa",
            "color": "#10b981",
            "desc": "Cánh hoa tiêu giảm, cấu trúc đài bao phát triển bảo vệ phấn hoa. Thuộc phân nhóm cổ điển thích nghi khí hậu lạnh.",
            "img": "setosa.jpg"
        },
        "Iris-versicolor": {
            "name": "Iris Versicolor",
            "badge": "badge-versicolor",
            "color": "#06b6d4",
            "desc": "Kích thước hình thái cân bằng hoàn hảo giữa lá đài và cánh hoa. Có khả năng thích nghi đầm lầy cao.",
            "img": "versicolor.jpg"
        },
        "Iris-virginica": {
            "name": "Iris Virginica",
            "badge": "badge-virginica",
            "color": "#f43f5e",
            "desc": "Tỉ lệ cánh hoa phát triển vượt trội với diện tích tiếp xúc lớn. Hệ gân cánh phân nhánh sẫm màu đặc trưng.",
            "img": "virginica.jpg"
        }
    }
    info = meta.get(species_tag, meta["Iris-versicolor"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📡 KẾT QUẢ SUY LUẬN TELEMETRY")

    col_res1, col_res2 = st.columns([1.2, 1])

    with col_res1:
        st.markdown(f"""
        <div class="cyber-panel" style="border-left: 6px solid {info['color']};">
            <span class="cyber-badge {info['badge']}">ĐÃ ĐỒNG BỘ ĐỊNH DANH</span>
            <h1 style="color: {info['color']}; font-size: 2.2rem; margin: 12px 0 6px 0;">{info['name']}</h1>
            <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.6;">{info['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Tính xác suất phân bố
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba([[sl, sw, pl, pw]])[0]
            st.markdown("""<div class="cyber-panel"><b>📊 Ma Trận Xác Suất Dự Đoán (Platt Scale Matrix)</b>""", unsafe_allow_html=True)
            names = ["Iris Setosa", "Iris Versicolor", "Iris Virginica"]
            for name, pr in zip(names, probs):
                st.write(f"• **{name}**: `{pr*100:.1f}%`")
                st.progress(float(pr))
            st.markdown("</div>", unsafe_allow_html=True)

    with col_res2:
        # Biểu đồ Radar tương tác 4 trục
        st.markdown("""<div class="cyber-panel"><b>🧭 Radar Chiếu Không Gian Hình Thái (Morpho-Space)</b>""", unsafe_allow_html=True)
        radar_fig = go.Figure()

        # Chuẩn hóa giá trị 4 chỉ số theo thang 0-100%
        # Chuẩn: sl (4-8), sw (2-4.5), pl (1-7), pw (0.1-2.5)
        norm_r = [
            (sl - 4.0) / 4.0 * 100,
            (sw - 2.0) / 2.5 * 100,
            (pl - 1.0) / 6.0 * 100,
            (pw - 0.1) / 2.4 * 100
        ]
        categories = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width']

        radar_fig.add_trace(go.Scatterpolar(
            r=norm_r,
            theta=categories,
            fill='toself',
            name='Mẫu hiện tại',
            line_color=info['color'],
            fillcolor=f"rgba({int(info['color'][1:3], 16)}, {int(info['color'][3:5], 16)}, {int(info['color'][5:7], 16)}, 0.35)"
        ))

        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#64748b"),
                angularaxis=dict(color="#cbd5e1"),
                bgcolor="rgba(15, 23, 42, 0.4)"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1"),
            margin=dict(l=35, r=35, t=25, b=25),
            showlegend=False
        )
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 50px; padding: 20px;">
    IRIS-SYNAPSE OS v3.2 • Powered by Support Vector Machines (SVM) & Streamlit Framework
</div>
""", unsafe_allow_html=True)