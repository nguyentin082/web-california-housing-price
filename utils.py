import ast
import joblib
import streamlit as st
import pandas as pd
import json
import numpy as np
import folium
from sklearn.preprocessing import RobustScaler


@st.cache_data
def load_data():
    return pd.read_csv("data/housing.csv")

@st.cache_data
def load_california_geojson():
    """Tải dữ liệu ranh giới California"""
    try:
        with open("data/california.geojson", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading geojson: {e}")
        return {}

@st.cache_data
def load_model():
    """Tải mô hình dự đoán giá nhà"""
    try:
        return joblib.load("models/best_xgb_model.pkl")
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


def create_folium_map(california_geojson):
    """Tạo bản đồ Folium với ranh giới California"""
    m = folium.Map(location=[37.5, -119.5], zoom_start=5)

    # Vẽ đường ranh giới California
    folium.GeoJson(
        california_geojson,
        name="California Boundary",
        style_function=lambda x: {
            "color": "green",
            "weight": 5,
            "fillColor": "lightblue",
            "fillOpacity": 0.2,
        },
    ).add_to(m)

    # Hiển thị điểm đã chọn
    for lat, lon in st.session_state["selected_locations"]:
        folium.Marker(
            location=[lat, lon],
            popup=f"📍 {lat}, {lon}",
            icon=folium.Icon(color="red", icon="cloud")
        ).add_to(m)

    return m



def get_user_input():
    """Nhận dữ liệu đầu vào từ người dùng"""
    st.write("### Enter House Features:")
    col1, col2 = st.columns(2)

    with col1:
        # lon = st.slider("Longitude", -124.35, -114.31)
        # lat = st.slider("Latitude", 32.54, 41.95)
        # st.session_state["selected_locations"] = [(lat, lon)]

        housing_median_age = st.slider("Housing Median Age (years)", 1, 52, value=33)
        total_rooms = st.slider("Total Rooms", 2, 39320, 1256)
        total_bedrooms = st.slider("Total Bedrooms", 1, 6445, 331)

    with col2:
        population = st.slider("Population", 1, 40000, 1315)
        households = st.slider("Households", 1, 6082, 321)
        median_income = st.slider("Median Income (measured in tens of thousands of US Dollars)", 0.4, 16.0, value=1.9)
        ocean_proximity = st.selectbox("Ocean Proximity", ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"], index=4)

    return process_features(housing_median_age, total_rooms, total_bedrooms, population, households, median_income, ocean_proximity)



def process_features(housing_median_age, total_rooms, total_bedrooms, population, households, median_income, ocean_proximity):
    """Xử lý các đặc trưng đầu vào và trả về DataFrame"""
    print("Adding columns: rooms_per_household, bedrooms_per_room, bedrooms_per_room")
    rooms_per_household = total_rooms / households if households else 0
    bedrooms_per_room = total_bedrooms / total_rooms if total_rooms else 0
    population_per_household = population / households if households else 0

    # Log Transform
    print("Log Transforming...")
    total_rooms = np.log1p(total_rooms)
    total_bedrooms = np.log1p(total_bedrooms)
    population = np.log1p(population)
    households = np.log1p(households)
    median_income = np.log1p(median_income)
    rooms_per_household = np.log1p(rooms_per_household)
    bedrooms_per_room = np.log1p(bedrooms_per_room)
    population_per_household = np.log1p(population_per_household)

    # One-hot Encoding cho ocean_proximity
    print("Onehot Encoding...")
    with open('dictionaries/ocean_encode_dict.txt', 'r') as f:
        ocean_mapping = ast.literal_eval(f.read())
    ocean_encoded = ocean_mapping.get(ocean_proximity, [0, 0, 0, 0])  # Tránh lỗi nếu giá trị không tồn tại
    print("Separating to ocean_proximity_INLAND, ocean_proximity_ISLAND, ocean_proximity_NEAR_BAY, ocean_proximity_NEAR_OCEAN")
    ocean_proximity_INLAND, ocean_proximity_ISLAND, ocean_proximity_NEAR_BAY, ocean_proximity_NEAR_OCEAN = ocean_encoded
    print("Done!!")

    # Tạo DataFrame chứa dữ liệu đầu vào
    df = pd.DataFrame([{
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income,
        "rooms_per_household": rooms_per_household,
        "bedrooms_per_room": bedrooms_per_room,
        "population_per_household": population_per_household,
        "ocean_proximity_INLAND": ocean_proximity_INLAND,
        "ocean_proximity_ISLAND": ocean_proximity_ISLAND,
        "ocean_proximity_NEAR BAY": ocean_proximity_NEAR_BAY,
        "ocean_proximity_NEAR OCEAN": ocean_proximity_NEAR_OCEAN
    }])

    return df


def predict_price(model, dataframe):

    """Dự đoán giá nhà"""
    if model is None:
        st.error("⚠ Model is not loaded. Please check the model file.")
        return

    if not st.session_state.get("selected_locations"):
        st.error("⚠ Please select a location on the map first!")
        return

    longitude, latitude = st.session_state["selected_locations"][-1]
    dataframe['longitude'] = longitude
    dataframe['latitude'] = latitude

    # st.write("Before scale")
    # st.table(dataframe)

    # Scaler
    num_features = ["longitude", "latitude", "housing_median_age", "total_rooms",
                    "total_bedrooms", "population", "households", "median_income",
                    "rooms_per_household", "bedrooms_per_room", "population_per_household"]
    cat_features = ["ocean_proximity_INLAND", "ocean_proximity_ISLAND", "ocean_proximity_NEAR BAY", "ocean_proximity_NEAR OCEAN"]

    scaler = joblib.load('scaler/robust_scaler.pkl')
    X_scaled = pd.DataFrame(scaler.transform(dataframe[num_features]), columns=num_features)
    X_scaled = pd.concat([X_scaled, dataframe[cat_features].reset_index(drop=True)], axis=1)

    # st.write("After Scale")
    # st.table(X_scaled)


    # Prediction

    try:
        predicted_price = np.expm1(model.predict(X_scaled)[0])
        st.success(f"🏡 Estimated House Price: **${predicted_price:,.2f}**")
    except Exception as e:
        st.error(f"⚠ Error during prediction: {e}")