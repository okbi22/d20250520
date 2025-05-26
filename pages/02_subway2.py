import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("subway_congestion.csv")
    return df

df = load_data()

# 지하철 역 위치 정보 (예제 데이터)
station_locations = {
    "강남역": [37.4979, 127.0276],
    "서울역": [37.5561, 126.9723],
    "홍대입구역": [37.5565, 126.9236],
    "건대입구역": [37.5404, 127.0702],
    "잠실역": [37.5139, 127.1023],
}

# UI - 첫 번째 역 선택
st.title("🚇 서울 지하철 혼잡도 비교 & 지도 표시")
st.subheader("두 개의 역을 선택하세요!")

selected_line_1 = st.selectbox("📌 첫 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line1")
selected_station_1 = st.selectbox("🚉 첫 번째 출발역을 선택하세요", sorted(df[df['호선'] == selected_line_1]['출발역'].unique()), key="station1")

selected_line_2 = st.selectbox("📌 두 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line2")
selected_station_2 = st.selectbox("🚉 두 번째 출발역을 선택하세요", sorted(df[df['호선'] == selected_line_2]['출발역'].unique()), key="station2")

selected_direction = st.selectbox("🚇 상하선 선택", sorted(df['상하구분'].unique()))

# 데이터 필터링
if selected_station_1 and selected_station_2:
    plot_data = df[
        ((df['호선'] == selected_line_1) & (df['출발역'] == selected_station_1)) |
        ((df['호선'] == selected_line_2) & (df['출발역'] == selected_station_2))
    ]
    plot_data = plot_data[plot_data['상하구분'] == selected_direction]

    time_columns = [col for col in df.columns if '시' in col]
    melted = plot_data.melt(id_vars=['출발역'], value_vars=time_columns,
                            var_name='시간', value_name='혼잡도')

    color_map = {selected_station_1: "red", selected_station_2: "blue"}

    # 막대 그래프 생성
    fig = px.bar(melted, x='시간', y='혼잡도', color='출발역', barmode="group",
                 title=f"{selected_station_1} (🔴) vs {selected_station_2} (🔵) 혼잡도 비교",
                 color_discrete_map=color_map,
                 labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})

    st.plotly_chart(fig, use_container_width=True)

    # 지도 생성
    st.subheader("🗺️ 선택한 역 지도 보기")
    m = folium.Map(location=[37.55, 126.98], zoom_start=12)  # 서울 중심 좌표

    # 첫 번째 역 마커 추가 (빨강)
    if selected_station_1 in station_locations:
        folium.Marker(
            location=station_locations[selected_station_1], 
            popup=f"{selected_station_1} ({selected_line_1}호선)", 
            icon=folium.Icon(color="red")
        ).add_to(m)

    # 두 번째 역 마커 추가 (파랑)
    if selected_station_2 in station_locations:
        folium.Marker(
            location=station_locations[selected_station_2], 
            popup=f"{selected_station_2} ({selected_line_2}호선)", 
            icon=folium.Icon(color="blue")
        ).add_to(m)

    # 지도 출력
    st_folium(m, width=800, height=500)

else:
    st.warning("⚠️ 두 개의 출발역을 선택하세요!")
