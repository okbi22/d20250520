import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("subway_congestion.csv")
    return df

df = load_data()

# UI 설정
st.title("서울 지하철 혼잡도 비교")

# 첫 번째 출발역 선택
selected_line1 = st.selectbox("첫 번째 호선 선택", sorted(df['호선'].unique()), key="line1")
selected_station1 = st.selectbox("첫 번째 출발역 선택", 
                                 sorted(df[df['호선'] == selected_line1]['출발역'].unique()), 
                                 key="station1")

# 두 번째 출발역 선택
selected_line2 = st.selectbox("두 번째 호선 선택", sorted(df['호선'].unique()), key="line2")
selected_station2 = st.selectbox("두 번째 출발역 선택", 
                                 sorted(df[df['호선'] == selected_line2]['출발역'].unique()), 
                                 key="station2")

selected_direction = st.selectbox("상하선 선택", sorted(df['상하구분'].unique()))

if selected_station1 and selected_station2:
    plot_data1 = df[(df['호선'] == selected_line1) & 
                    (df['출발역'] == selected_station1) & 
                    (df['상하구분'] == selected_direction)]
    
    plot_data2 = df[(df['호선'] == selected_line2) & 
                    (df['출발역'] == selected_station2) & 
                    (df['상하구분'] == selected_direction)]

    time_columns = [col for col in df.columns if '시' in col]
    
    melted1 = plot_data1.melt(id_vars=['출발역'], value_vars=time_columns, 
                              var_name='시간', value_name='혼잡도')
    
    melted2 = plot_data2.melt(id_vars=['출발역'], value_vars=time_columns, 
                              var_name='시간', value_name='혼잡도')

    # 그래프 생성
    fig1 = px.bar(melted1, x='시간', y='혼잡도', color_discrete_sequence=['red'],
                  title=f"{selected_station1} 혼잡도", labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})
    
    fig2 = px.bar(melted2, x='시간', y='혼잡도', color_discrete_sequence=['blue'],
                  title=f"{selected_station2} 혼잡도", labels={"혼잡도": "혼잡도 (비율)", "시간": "시간대"})

    # Streamlit에 두 개의 그래프 표시
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("각 호선에서 하나씩 출발역을 선택하세요!")
