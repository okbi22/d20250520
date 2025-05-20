import streamlit as st
from geopy.geocoders import Nominatim
import pandas as pd
import pydeck as pdk

st.title("장소 지도 표시기")

place = st.text_input("장소를 입력하세요:", "서울")

if place:
    geolocator = Nominatim(user_agent="place_locator")
    location = geolocator.geocode(place)

    if location:
        st.write(f"**{place}**의 위치: {location.latitude}, {location.longitude}")

        # 지도에 표시
        df = pd.DataFrame({'lat': [location.latitude], 'lon': [location.longitude]})

        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=location.latitude,
                longitude=location.longitude,
                zoom=12,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=100,
                ),
            ],
        ))
    else:
        st.error("위치를 찾을 수 없습니다.")
