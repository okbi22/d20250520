import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# --- 1. 데이터 불러오기 및 전처리 ---
@st.cache_data
def load_data():
    df = pd.read_csv("subway_congestion.csv")
    return df

df = load_data()

# --- 2. 역 좌표 데이터 (예시) ---
# 실제 앱에서는 역 ID와 매칭되는 별도의 CSV 파일 등에서 불러오는 것이 좋습니다.
# 여기서는 예시로 몇 개의 주요 역만 정의합니다.
# 데이터 출처: 서울열린데이터광장 등 (정확한 좌표는 별도 확인 필요)
station_coordinates = {
    "상일동": [37.5574, 127.1722], # 5호선 상일동역
    "고덕": [37.5559, 127.1620],   # 5호선 고덕역
    "강남": [37.4981, 127.0276],   # 2호선 강남역
    "잠실": [37.5133, 127.1003],   # 2호선/8호선 잠실역
    "서울역": [37.5562, 126.9723], # 1호선/4호선/경의중앙/공항철도 서울역
    "신도림": [37.5088, 126.8912], # 1호선/2호선 신도림역
    "왕십리": [37.5610, 127.0376], # 2호선/5호선/분당선/경의중앙 왕십리역
    "사당": [37.4766, 126.9817],   # 2호선/4호선 사당역
    "홍대입구": [37.5577, 126.9234], # 2호선/공항철도/경의중앙 홍대입구역
    "명동": [37.5609, 126.9863],   # 4호선 명동역
    "가산디지털단지": [37.4795, 126.8829], # 1호선/7호선 가산디지털단지역
    "종로3가": [37.5704, 126.9922], # 1호선/3호선/5호선 종로3가역
    "선릉": [37.5045, 127.0489], # 2호선/분당선 선릉역
    "을지로입구": [37.5663, 126.9829] # 2호선 을지로입구역
}

# --- 3. Streamlit UI ---
st.title("🚇 서울 지하철 혼잡도 비교 및 위치 확인")
st.subheader("두 개의 역을 선택하여 혼잡도를 비교하고 지도에서 위치를 확인하세요!")

# 사이드바에 역 선택 UI 배치
with st.sidebar:
    st.header("첫 번째 역 선택")
    selected_line_1 = st.selectbox("📌 첫 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line1")
    selected_station_1 = st.selectbox("🚉 첫 번째 출발역을 선택하세요",
                                     sorted(df[df['호선'] == selected_line_1]['출발역'].unique()), key="station1")

    st.header("두 번째 역 선택")
    selected_line_2 = st.selectbox("📌 두 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line2")
    selected_station_2 = st.selectbox("🚉 두 번째 출발역을 선택하세요",
                                     sorted(df[df['호선'] == selected_line_2]['출발역'].unique()), key="station2")

    st.header("기타 옵션")
    selected_direction = st.selectbox("🚇 상하선 선택", sorted(df['상하구분'].unique()))


# --- 4. 혼잡도 그래프 생성 ---
if selected_station_1 and selected_station_2:
    plot_data = df[
        ((df['호선'] == selected_line_1) & (df['출발역'] == selected_station_1)) |
        ((df['호선'] == selected_line_2) & (df['출발역'] == selected_station_2))
    ]
    plot_data = plot_data[plot_data['상하구분'] == selected_direction]

    # 시간대 컬럼 추출
    time_columns = [col for col in df.columns if '시' in col]

    # 데이터 변형
    melted = plot_data.melt(id_vars=['출발역'], value_vars=time_columns, var_name='시간', value_name='혼잡도')

    # 색상 지정
    # plotly는 기본적으로 정해진 색상 팔레트가 있으나, 특정 색상 지정을 위해 color_discrete_map 사용
    color_map = {selected_station_1: "red", selected_station_2: "blue"}

    # 막대 그래프 생성
    fig = px.bar(melted, x='시간', y='혼잡도', color='출발역', barmode="group",
                 title=f"**{selected_station_1}** (🔴) vs **{selected_station_2}** (🔵) 혼잡도 비교",
                 color_discrete_map=color_map,
                 labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"},
                 text='혼잡도') # 막대 위에 혼잡도 값 표시
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside') # 텍스트 포맷 및 위치 조정
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide') # 텍스트가 너무 많을 경우 숨김
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Folium 지도 생성 ---
    st.subheader("📍 선택한 역의 위치")

    # 서울 중심 좌표를 기준으로 초기 지도 생성
    # (선택된 역들이 지도에 없으면 오류가 날 수 있으므로, 초기 지도는 서울 중심이 안전)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

    # 첫 번째 역 마커 추가
    if selected_station_1 in station_coordinates:
        lat1, lon1 = station_coordinates[selected_station_1]
        folium.Marker(
            [lat1, lon1],
            popup=f"<b>{selected_station_1}</b> (첫 번째 역)",
            tooltip=selected_station_1,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
    else:
        st.warning(f"⚠️ **{selected_station_1}** 역의 좌표 정보가 없습니다. 지도를 표시할 수 없습니다.")

    # 두 번째 역 마커 추가
    if selected_station_2 in station_coordinates:
        lat2, lon2 = station_coordinates[selected_station_2]
        folium.Marker(
            [lat2, lon2],
            popup=f"<b>{selected_station_2}</b> (두 번째 역)",
            tooltip=selected_station_2,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
    else:
        st.warning(f"⚠️ **{selected_station_2}** 역의 좌표 정보가 없습니다. 지도를 표시할 수 없습니다.")

    # 지도를 Streamlit에 표시
    folium_static(m)

else:
    st.warning("⚠️ 두 개의 출발역을 선택하세요!")
