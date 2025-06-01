import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# 📁 데이터 로드
df = pd.read_csv("subway_congestion.csv")

# 📌 요일 선택
day_option = st.selectbox("📅 요일 선택", ["평일", "토요일", "일요일"])

# 📌 상하선 필터 (원하면 추가 가능)
df_filtered = df[(df['요일구분'] == day_option) & (df['상하구분'] == '상선')]

# 🕒 시간대 컬럼 (30분 단위)
time_cols_30min = df.columns[6:]

# ⏱ 1시간 단위로 평균낼 쌍 구성
time_pairs = [(time_cols_30min[i], time_cols_30min[i + 1]) for i in range(0, len(time_cols_30min)-1, 2)]

# x축 라벨 정제: 5시, 6시, ..., 23시
hour_labels = [col1[:col1.find('시') + 1] for col1, _ in time_pairs]

# 🖱️ 역 선택
station_list = sorted(df_filtered['출발역'].unique())
station1 = st.selectbox("🔵 첫 번째 역 선택", station_list)
station2 = st.selectbox("🟠 두 번째 역 선택", station_list, index=1)

# 평균 혼잡도 계산 함수
def get_hourly_avg(station_name):
    row = df_filtered[df_filtered['출발역'] == station_name][time_cols_30min].mean()
    return [row[[col1, col2]].mean() for col1, col2 in time_pairs]

# 데이터 계산
hourly_avg1 = get_hourly_avg(station1)
hourly_avg2 = get_hourly_avg(station2)

# 🖼️ 제목 및 설명
st.title("🚇 서울 지하철 역 혼잡도 비교")

st.markdown(f"""
#### 📊 데이터 설명  
서울교통공사 1-8호선 **30분 단위 평균 혼잡도**를 바탕으로  
30분간 지나는 열차들의 평균 혼잡도 (정원 대비 승차 인원 비율)를 1시간 단위로 집계한 결과입니다.  
승객 수와 좌석 수가 같을 경우를 혼잡도 **34%**로 간주합니다.

- 선택한 요일: **{day_option}**
- 데이터 단위: 1시간 평균 혼잡도 (%)
""")

# 📊 Plotly 그래프
fig = go.Figure()

fig.add_trace(go.Bar(
    x=hour_labels,
    y=hourly_avg1,
    name=station1,
    marker_color='royalblue'
))

fig.add_trace(go.Bar(
    x=hour_labels,
    y=hourly_avg2,
    name=station2,
    marker_color='darkorange'
))

fig.update_layout(
    barmode='group',
    title=f"🕐 1시간 단위 혼잡도 비교: {station1} vs {station2} ({day_option})",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    xaxis_tickangle=0,
    height=600
)

st.plotly_chart(fig)
