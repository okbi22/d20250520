import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("subway_congestion.csv")
    return df

df = load_data()

# UI - 첫 번째 역 선택
st.title("🚇 서울 지하철 혼잡도 비교")
st.subheader("두 개의 역을 선택하여 비교하세요!")

selected_line_1 = st.selectbox("📌 첫 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line1")
selected_station_1 = st.selectbox("🚉 첫 번째 출발역을 선택하세요", sorted(df[df['호선'] == selected_line_1]['출발역'].unique()), key="station1")

# UI - 두 번째 역 선택
selected_line_2 = st.selectbox("📌 두 번째 호선을 선택하세요", sorted(df['호선'].unique()), key="line2")
selected_station_2 = st.selectbox("🚉 두 번째 출발역을 선택하세요", sorted(df[df['호선'] == selected_line_2]['출발역'].unique()), key="station2")

# 상하선 선택
selected_direction = st.selectbox("🚇 상하선 선택", sorted(df['상하구분'].unique()))

# 데이터 필터링
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
    color_map = {selected_station_1: "red", selected_station_2: "blue"}

    # 막대 그래프 생성
    fig = px.bar(melted, x='시간', y='혼잡도', color='출발역', barmode="group",
                 title=f"{selected_station_1} (🔴) vs {selected_station_2} (🔵) 혼잡도 비교",
                 color_discrete_map=color_map,
                 labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ 두 개의 출발역을 선택하세요!")
