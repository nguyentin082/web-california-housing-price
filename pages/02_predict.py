import streamlit as st
from streamlit_folium import st_folium
import folium
from utils import load_california_geojson, load_model, get_user_input, predict_price, \
    process_features, create_folium_map

# Cấu hình trang Streamlit
st.set_page_config(page_title="Prediction", layout="wide", initial_sidebar_state="collapsed")
st.title("🏡 House Price Prediction")
st.write("Click on the map to select a location.")

# ====================== LOAD DATA & MODEL ======================
model = load_model()
california_geojson = load_california_geojson()

# ====================== SESSION STATE ======================
if "selected_locations" not in st.session_state:
    st.session_state["selected_locations"] = []

# ====================== TẠO BẢN ĐỒ =====================

# **Hiển thị bản đồ lần đầu**
map_object = create_folium_map(california_geojson)
map_data = st_folium(map_object, height=500, width=700, key="house_map")

# ================== XỬ LÝ SỰ KIỆN CLICK ==================
if map_data and map_data["last_clicked"]:
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]

    # Kiểm tra nếu tọa độ chưa có thì thêm vào danh sách
    if (lat, lon) not in st.session_state["selected_locations"]:
        st.session_state["selected_locations"] = [(lat, lon)]  # 🔥 Chỉ giữ 1 điểm mới nhất

    # 🔥 **Render lại bản đồ ngay lập tức**
    st.rerun()  # 👈 Dùng st.rerun() để cập nhật ngay bản đồ mà không cần reload toàn bộ trang

# ====================== HIỂN THỊ DANH SÁCH ĐIỂM ======================
if st.session_state["selected_locations"]:
    lat, lon = st.session_state["selected_locations"][0]
    st.write(f"📍 **Your location ping:** {lat}, {lon}")



# ====================== NHẬN DỮ LIỆU ĐẦU VÀO & PREPROCESS ======================
df = get_user_input()

# In toàn bộ giá trị
# st.table(df)

# # ====================== NÚT DỰ ĐOÁN ======================
if st.button("🔍 Predict Price"):
    predict_price(model, df)




# Ẩn sidebar bằng CSS
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)