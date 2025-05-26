import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("subway_congestion.csv")
    return df

df = load_data()

# UI - 역, 노선 선택
st.title("서울 지하철 혼잡도 비교")

selected_line = st.selectbox("호선을 선택하세요", sorted(df['호선'].unique()))
selected_direction = st.selectbox("상하선 선택", sorted(df['상하구분'].unique()))
selected_stations = st.multiselect("비교할 두 개의 출발역을 선택하세요", 
                                   sorted(df[df['호선'] == selected_line]['출발역'].unique()), 
                                   max_selections=2)

if len(selected_stations) == 2:
    plot_data = df[
        (df['호선'] == selected_line) & 
        (df['출발역'].isin(selected_stations)) & 
        (df['상하구분'] == selected_direction)
    ]

    time_columns = [col for col in df.columns if '시' in col]
    melted = plot_data.melt(id_vars=['출발역'], value_vars=time_columns,
                            var_name='시간', value_name='혼잡도')

    fig = px.line(melted, x='시간', y='혼잡도', color='출발역',
                  title=f"{selected_stations[0]} vs {selected_stations[1]} 혼잡도 비교",
                  labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("두 개의 출발역을 선택하세요!")
