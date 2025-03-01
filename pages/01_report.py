import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from keplergl import KeplerGl
from utils import load_data, load_california_geojson

# TODO: Cấu hình trang
st.set_page_config(page_title="Report", layout="wide", initial_sidebar_state="collapsed")

st.title("📊 California Housing Price Report")
st.write("Analyzing and visualizing key insights from the housing dataset")

# TODO: Load dataset
df = load_data()

# TODO: Mô tả dữ liệu
st.subheader("📜 Data Description")
desc = {
    "longitude": "House location (west-east)",
    "latitude": "House location (north-south)",
    "housingMedianAge": "Median age of houses in a block",
    "totalRooms": "Total rooms in a block",
    "totalBedrooms": "Total bedrooms in a block",
    "population": "Total population in a block",
    "households": "Total households in a block",
    "medianIncome": "Median household income ($10,000s)",
    "medianHouseValue": "Median house value ($)",
    "oceanProximity": "Proximity to ocean"
}
st.dataframe(pd.DataFrame(desc.items(), columns=["Feature", "Description"]), hide_index=True)

# TODO: Hiển thị dữ liệu gốc và thống kê tổng quan
st.subheader("📜 Raw Data")
st.dataframe(df.head(10))
st.subheader("📜 Data Summary")
st.write(df.describe())

# TODO: Biểu đồ histogram cho dữ liệu số
st.subheader("📊 Numerical Data Distribution")
num_cols = df.select_dtypes(include=['number']).columns
cols = st.columns(3)

for i, col in enumerate(num_cols):
    with cols[i % 3]:
        fig = px.histogram(df, x=col, nbins=30, barmode="group", title=f"{col.replace('_', ' ').title()} Histogram")
        fig.update_layout(width=600, height=400, bargap=0.03)
        st.plotly_chart(fig, use_container_width=True)

# TODO: Biểu đồ dữ liệu phân loại
st.subheader("📊 Categorical Data Distribution")
st.bar_chart(df["ocean_proximity"].value_counts())

# TODO: Heatmap tương quan đặc trưng
st.subheader("📊 Feature Correlation Heatmap")
correlation_matrix = df.corr(numeric_only=True)

fig = go.Figure(data=go.Heatmap(
    z=correlation_matrix.values,
    x=correlation_matrix.columns,
    y=correlation_matrix.index,
    colorscale="YlGnBu",
    text=correlation_matrix.round(2).values,
    texttemplate="%{text}",
    textfont={"size": 14}
))
fig.update_layout(height=700)
st.plotly_chart(fig, use_container_width=False)


# TODO: Khởi tạo bản đồ
st.subheader("📍 Geographical Distribution of Houses")
# Đọc dữ liệu ranh giới California từ file GeoJSON
california_geojson = load_california_geojson()

# Tạo DataFrame với tọa độ nhà ở
geo_df = df[["longitude", "latitude", "median_house_value"]]

# Khởi tạo bản đồ Kepler
map_kepler = KeplerGl(height=600)

# Thêm dữ liệu nhà ở
map_kepler.add_data(data=geo_df, name="California Housing")

# Cấu hình để hiển thị ranh giới bang California
map_kepler.config = {
    "version": "v1",
    "config": {
        "mapState": {
            "latitude": 37.5,  # Trung tâm California
            "longitude": -119.5,
            "zoom": 4,  # Zoom xa hơn
            "pitch": 0,
            "bearing": 0
        },
        "visState": {
            "layers": [
                {
                    "id": "boundary-layer",
                    "type": "geojson",
                    "config": {
                        "dataId": "California Boundary",
                        "label": "California Boundary",
                        "strokeColor": [255, 255, 255],  # Viền trắng
                        "strokeWidth": 2,
                        "filled": True,
                        "fillColor": [0, 128, 255, 80]  # Màu nền với độ trong suốt 80
                    }
                }
            ]
        }
    }
}

# Load dữ liệu ranh giới vào Kepler
map_kepler.add_data(data=california_geojson, name="California Boundary")

# Hiển thị bản đồ trong Streamlit
st.components.v1.html(map_kepler._repr_html_(), height=500)








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