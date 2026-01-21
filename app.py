import streamlit as st
import json
from pathlib import Path

import folium
from streamlit_folium import st_folium

from map.map_builder import build_map
from pdf.pdf_generator import generate_pdf

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="가족 일본여행 지도", layout="wide")
st.title("🗾 가족 일본 자유여행 일정 지도")

DATA_PATH = Path("data/schedule.json")

# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "schedule" not in st.session_state:
    if DATA_PATH.exists():
        st.session_state.schedule = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    else:
        st.session_state.schedule = []

if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

# -----------------------------
# 좌측: 일정 입력
# -----------------------------
st.sidebar.header("✍️ 일정 추가")

with st.sidebar.form("add_event"):
    day = st.number_input("Day", min_value=1, step=1)

    title_ko = st.text_input("장소명 (한글)")
    title_ja = st.text_input("장소명 (일본어, 선택)")

    event_type = st.selectbox("유형", ["숙소", "관광", "이동", "휴식", "미확정"])
    memo = st.text_area("메모 (어르신용 한 줄 설명)")

    # 좌표 표시 (읽기 전용)
    if st.session_state.selected_location:
        lat, lon = st.session_state.selected_location
        st.text_input("위도", value=f"{lat:.6f}", disabled=True)
        st.text_input("경도", value=f"{lon:.6f}", disabled=True)
    else:
        st.text_input("위도", value="(지도에서 클릭하세요)", disabled=True)
        st.text_input("경도", value="", disabled=True)

    submitted = st.form_submit_button("➕ 일정 추가")

    if submitted:
        if not title_ko:
            st.error("장소명(한글)은 필수입니다.")
            st.stop()

        if not st.session_state.selected_location:
            st.error("오른쪽 지도에서 위치를 먼저 선택해주세요.")
            st.stop()

        lat, lon = st.session_state.selected_location

        st.session_state.schedule.append({
            "id": f"{day}_{title_ko}",
            "day": day,
            "title_ko": title_ko,
            "title_ja": title_ja.strip() if title_ja.strip() else None,
            "type": event_type,
            "lat": lat,
            "lon": lon,
            "memo": memo
        })

        DATA_PATH.write_text(
            json.dumps(st.session_state.schedule, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        st.session_state.selected_location = None
        st.success("일정이 추가되었습니다.")

# -----------------------------
# 우측 상단: 위치 선택 지도
# -----------------------------
st.subheader("📍 지도에서 위치 선택 (클릭)")

click_map = folium.Map(
    location=[33.5, 130.5],
    zoom_start=8,
    tiles="cartodbpositron"
)

# 이미 선택된 위치가 있으면 표시
if st.session_state.selected_location:
    folium.Marker(
        st.session_state.selected_location,
        icon=folium.Icon(color="red")
    ).add_to(click_map)

map_result = st_folium(
    click_map,
    height=400,
    width=700,
    returned_objects=["last_clicked"]
)

if map_result and map_result["last_clicked"]:
    st.session_state.selected_location = [
        map_result["last_clicked"]["lat"],
        map_result["last_clicked"]["lng"]
    ]
    st.success("📍 위치가 선택되었습니다.")

# -----------------------------
# 전체 일정 지도
# -----------------------------
st.subheader("🗺️ 여행 전체 동선 지도")

travel_map = build_map(st.session_state.schedule)
st.components.v1.html(travel_map._repr_html_(), height=600)

# -----------------------------
# PDF 생성
# -----------------------------
st.subheader("📄 여행 일정 PDF")

if st.button("📄 여행 지도 PDF 만들기"):
    pdf_path = generate_pdf(st.session_state.schedule)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 PDF 다운로드",
            data=f,
            file_name="가족_일본여행_지도.pdf",
            mime="application/pdf"
        )
