import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="🏡 AI-Powered California Housing Price Prediction",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Tạo tiêu đề đẹp mắt với Markdown
st.markdown(
    "<h1 style='text-align: center; color: #2E86C1;'>🏡 AI-Powered California Housing Price Prediction</h1>",
    unsafe_allow_html=True
)

# Mô tả ứng dụng
st.markdown(
    "<p style='text-align: center; font-size:18px;'>Leverage AI to analyze and predict California housing prices with real-time insights.</p>",
    unsafe_allow_html=True
)

st.divider()

# Chia bố cục thành 2 cột
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 California Housing Price Report")
    st.markdown(
        "Get a detailed analysis of the current housing market trends in California."
    )
    if st.button("View Report"):
        st.switch_page("pages/01_report.py")

with col2:
    st.markdown("### 🏡 House Price Prediction")
    st.markdown(
        "Use AI to estimate the price of a house based on key features and market data."
    )
    if st.button("Predict Price"):
        st.switch_page("pages/02_predict.py")

# Thêm footer hoặc logo (nếu cần)
st.markdown("<br><hr style='border:1px solid #ccc;'><p style='text-align:center;'>Powered by AI & Streamlit</p>", unsafe_allow_html=True)