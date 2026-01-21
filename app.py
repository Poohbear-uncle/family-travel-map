import streamlit as st
from map.map_builder import build_map
from pdf.pdf_generator import generate_pdf
import json
from pathlib import Path

DATA_PATH = Path("data/schedule.json")

st.set_page_config(page_title="가족 일본여행 지도", layout="wide")

st.title("🗾 가족 일본 자유여행 일정 지도")

# 데이터 로드
if DATA_PATH.exists():
    schedule = json.loads(DATA_PATH.read_text(encoding="utf-8"))
else:
    schedule = []

# -------------------------------
# 일정 입력
# -------------------------------
st.sidebar.header("✍️ 일정 추가")

with st.sidebar.form("add_event"):
    day = st.number_input("Day", min_value=1, step=1)
    title_ko = st.text_input("장소명 (한글)")
    title_ja = st.text_input("장소명 (일본어)")
    lat = st.number_input("위도", format="%.6f")
    lon = st.number_input("경도", format="%.6f")
    event_type = st.selectbox("유형", ["숙소", "관광", "이동", "휴식", "미확정"])
    memo = st.text_area("메모 (어르신용)")
    submitted = st.form_submit_button("추가")

    if submitted:
        schedule.append({
            "id": f"{day}_{title_ko}",
            "day": day,
            "title_ko": title_ko,
            "title_ja": title_ja,
            "type": event_type,
            "lat": lat,
            "lon": lon,
            "memo": memo
        })
        DATA_PATH.write_text(json.dumps(schedule, ensure_ascii=False, indent=2), encoding="utf-8")
        st.success("일정이 추가되었습니다.")

# -------------------------------
# 지도 표시
# -------------------------------
st.subheader("🗺️ 여행 동선 지도")
travel_map = build_map(schedule)
st.components.v1.html(travel_map._repr_html_(), height=600)

# -------------------------------
# PDF 생성
# -------------------------------
if st.button("📄 여행 지도 PDF 만들기"):
    pdf_path = generate_pdf(schedule)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 PDF 다운로드",
            data=f,
            file_name="가족_일본여행_지도.pdf",
            mime="application/pdf"
        )
