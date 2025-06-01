import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time # 지오코딩 요청 간 딜레이를 주기 위함

# 📁 데이터 로드
# @st.cache_data 데코레이터는 Streamlit이 함수 호출 결과를 캐시하여
# 앱이 다시 실행될 때마다 데이터를 다시 로드하지 않도록 합니다.
# ttl (Time To Live) 인자를 추가하여 캐시 유효 시간을 설정할 수 있습니다 (예: 1시간 = 3600초)
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv("subway_congestion.csv")
        return df
    except FileNotFoundError:
        st.error("오류: 'subway_congestion.csv' 파일을 찾을 수 없습니다. 파일이 올바른 위치에 있는지 확인하세요.")
        st.stop() # 파일이 없으면 앱 실행 중단
    except Exception as e:
        st.error(f"오류: CSV 파일을 읽는 중 문제가 발생했습니다. {e}")
        st.stop()

df = load_data()

# ✅ 앱 상단 제목 꾸미기
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>
        🚇 서울 지하철 혼잡도 비교 대시보드
    </h1>
    <h4 style='text-align: center; color: gray;'>
        지하철 역별 1시간 단위 혼잡도를 시각화하고 지도에서 위치를 확인해보세요!
    </h4>
    <hr>
""", unsafe_allow_html=True)

# ✅ 요일 및 역 선택
st.subheader("📅 요일 및 역 선택")
day_option = st.selectbox("요일을 선택하세요", ["평일", "토요일", "일요일"])

# 선택된 요일과 상하선(상선 고정)에 따라 데이터 필터링
df_filtered = df[(df['요일구분'] == day_option) & (df['상하구분'] == '상선')]

# 필터링된 데이터에서 유니크한 역 목록 가져오기
station_list = sorted(df_filtered['출발역'].unique())

# station_list가 비어있지 않은지 확인하여 index 오류 방지
if not station_list:
    st.warning("⚠️ 선택된 요일 및 상하선에 해당하는 역 데이터가 없습니다. 다른 조건을 선택해주세요.")
    st.stop() # 역 데이터가 없으면 앱 실행 중단

station1 = st.selectbox("🔵 첫 번째 역 선택", station_list, index=0) # 첫 번째 역 기본값 설정
# 두 번째 역 선택 시, 첫 번째 역과 다른 역을 기본값으로 지정 (인덱스 범위 확인)
default_index2 = 1 if len(station_list) > 1 else 0
station2 = st.selectbox("🟠 두 번째 역 선택", station_list, index=default_index2)


# ✅ 시간대 컬럼 및 1시간 단위 평균 계산
time_cols_30min = df.columns[6:] # '00:00:00~00:30:00' 같은 형식의 컬럼들
time_pairs = []
# 30분 단위 컬럼이 2개 이상일 때만 시간 쌍 생성
if len(time_cols_30min) >= 2:
    time_pairs = [(time_cols_30min[i], time_cols_30min[i + 1]) for i in range(0, len(time_cols_30min) - 1, 2)]
else:
    st.warning("경고: 30분 단위 시간 컬럼이 충분하지 않아 시간대별 혼잡도 계산이 어렵습니다.")
    # 적절한 대체 로직 또는 오류 처리 필요

hour_labels = [col1[:col1.find('시') + 1] if '시' in col1 else col1 for col1, _ in time_pairs]


def get_hourly_avg(station_name):
    # 선택된 역의 데이터가 df_filtered에 존재하는지 확인
    if station_name not in df_filtered['출발역'].unique():
        return [0] * len(hour_labels) # 데이터가 없으면 0으로 채워진 리스트 반환
    
    # .loc를 사용하여 복사본 경고 방지 및 특정 역 데이터만 선택
    row_data = df_filtered.loc[df_filtered['출발역'] == station_name, time_cols_30min]
    
    if row_data.empty:
        return [0] * len(hour_labels) # 데이터가 없으면 0으로 채워진 리스트 반환

    # 여러 행이 있을 경우를 대비해 평균 사용
    row_mean = row_data.mean() 
    
    # 1시간 단위 평균 계산
    hourly_avg = []
    for col1, col2 in time_pairs:
        # col1, col2가 row_mean에 있는지 확인하여 KeyError 방지
        if col1 in row_mean.index and col2 in row_mean.index:
            hourly_avg.append(row_mean[[col1, col2]].mean())
        else:
            hourly_avg.append(0) # 해당 시간대 데이터가 없으면 0으로 처리

    return hourly_avg

hourly_avg1 = get_hourly_avg(station1)
hourly_avg2 = get_hourly_avg(station2)


# ✅ 혼잡도 그래프 시각화
st.markdown("### 📊 혼잡도 비교 그래프")
fig = go.Figure()
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg1, name=station1, marker_color='royalblue'))
fig.add_trace(go.Bar(x=hour_labels, y=hourly_avg2, name=station2, marker_color='darkorange'))

fig.update_layout(
    barmode='group',
    title=f"🕐 1시간 단위 혼잡도 비교: {station1} vs {station2} ({day_option})",
    xaxis_title="시간대",
    yaxis_title="혼잡도 (%)",
    xaxis_tickangle=0,
    height=600
)
st.plotly_chart(fig)

# ✅ 데이터 설명
st.markdown(f"""
#### 🧾 데이터 설명
서울교통공사 1-8호선 **30분 단위 평균 혼잡도** 데이터를 바탕으로,
30분간 지나는 열차들의 혼잡도를 1시간 평균으로 변환해 비교합니다.
- **정원 대비 승차 인원 비율**을 기준으로 하며,
- 승객 수 = 좌석 수일 때 혼잡도는 **34%**입니다.

📌 현재 선택 요일: **{day_option}**
""")

# --- Geopy를 이용한 지도 시각화 부분 ---
st.markdown("---")
st.markdown("### 🗺️ 선택한 역의 지도 위치")

# Geopy Nominatim 지오코더 초기화
# user_agent는 고유한 이름으로 설정하는 것이 좋습니다.
geolocator = Nominatim(user_agent="subway_congestion_app_2024")
# RateLimiter를 사용하여 요청 간 딜레이를 주어 서비스 약관 위반 방지
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# 캐싱을 이용하여 지오코딩 결과를 저장하여 불필요한 API 호출 방지
@st.cache_data(ttl=86400) # 24시간 캐시
def get_coords(station_name):
    try:
        # 역 이름에 "역 서울"을 추가하여 더 정확한 검색 유도
        location = geocode(f"{station_name}역 서울", timeout=10) 
        if location:
            return location.latitude, location.longitude
        else:
            # "역"을 붙여서 검색 실패 시, "지하철역"을 붙여서 재시도
            location = geocode(f"{station_name}지하철역 서울", timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                st.warning(f"⚠️ '{station_name}' 역의 좌표를 찾을 수 없습니다. (지오코딩 실패)")
                return None, None
    except Exception as e:
        st.warning(f"⚠️ '{station_name}' 역 지오코딩 중 오류 발생: {e}")
        return None, None

# 기본 서울 중심 좌표
center_lat, center_lon = 37.5665, 126.9780
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

found_coords_count = 0
coords_list = [] # 지도 중앙을 계산하기 위한 좌표 리스트

for station in [station1, station2]:
    lat, lon = get_coords(station)
    if lat is not None and lon is not None:
        coords_list.append([lat, lon])
        found_coords_count += 1
        color = "blue" if station == station1 else "orange"
        folium.Marker(
            location=[lat, lon],
            popup=f"{station}역",
            tooltip="📍 " + station,
            icon=folium.Icon(color=color)
        ).add_to(m)

# 두 역의 좌표를 모두 찾았다면 지도의 중심을 두 역의 중간으로 조정
if found_coords_count == 2:
    avg_lat = (coords_list[0][0] + coords_list[1][0]) / 2
    avg_lon = (coords_list[0][1] + coords_list[1][1]) / 2
    m.location = [avg_lat, avg_lon]
    # 두 역이 너무 멀리 떨어져 있지 않으면 줌 레벨을 더 확대
    # 간단한 거리 계산 (두 점 사이의 경도/위도 차이)
    lat_diff = abs(coords_list[0][0] - coords_list[1][0])
    lon_diff = abs(coords_list[0][1] - coords_list[1][1])
    if lat_diff < 0.05 and lon_diff < 0.05: # 대략 5km 이내
        m.zoom_start = 14
    elif lat_diff < 0.1 and lon_diff < 0.1: # 대략 10km 이내
        m.zoom_start = 13
    else:
        m.zoom_start = 12 # 넓은 지역 커버

elif found_coords_count == 1:
    m.location = coords_list[0] # 한 역만 찾았으면 해당 역으로 중심 이동
    m.zoom_start = 14 # 해당 역 주변 확대
else:
    # 좌표를 하나도 찾지 못했을 경우 기본 중심 유지
    pass


# Streamlit에 Folium 지도 표시
st_folium(m, width=700, height=500)

st.markdown("""
<br>
<small style='color:gray;'>
지도 데이터는 OpenStreetMap을 기반으로 하며, 지오코딩 결과는 실제와 약간의 차이가 있을 수 있습니다. <br>
API 호출 제한으로 인해 지오코딩 요청에 약간의 지연이 있을 수 있습니다.
</small>
""", unsafe_allow_html=True)
