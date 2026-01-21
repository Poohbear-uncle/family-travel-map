import streamlit as st
from streamlit_folium import st_folium
from map.map_builder import build_map
from utils.geocode import geocode_place

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="가족 여행 일정 지도", layout="wide")
st.title("🧳 가족 여행 일정 지도")
st.caption("검색 → 지도 중심 선택 → 일정 추가 → PDF 출력")

# -------------------------
# 세션 상태
# -------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "map_center" not in st.session_state:
    st.session_state.map_center = (33.5902, 130.4017)  # 후쿠오카 근처

if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

# -------------------------
# 레이아웃
# -------------------------
left, right = st.columns([1, 2])

# ===== 왼쪽 =====
with left:
    st.subheader("➕ 일정 입력")

    # 🔍 검색
    search_query = st.text_input(
        "🔍 장소 검색 (한글 / 일본어)",
        placeholder="예: 후쿠오카 공항, 糸島, 雷山千如寺"
    )

    if st.button("📡 검색해서 지도 이동"):
        result = geocode_place(search_query)
        if result:
            st.session_state.map_center = result
            st.success("지도 이동 완료")
        else:
            st.warning("검색 결과를 찾을 수 없습니다.")

    name_ko = st.text_input("장소명 (한글)")
    name_ja = st.text_input("장소명 (일본어, 선택)")
    start = st.text_input("시작 시간 (선택)")
    end = st.text_input("종료 시간 (선택)")
    note = st.text_area("메모", height=80)

    st.markdown("### 📍 선택된 위치")
    if st.session_state.selected_location:
        lat, lng = st.session_state.selected_location
        st.success(f"위도 {lat:.5f}, 경도 {lng:.5f}")
    else:
        st.info("오른쪽 지도 중심을 선택하세요.")

    if st.button("📌 일정 추가", use_container_width=True):
        if not name_ko or not st.session_state.selected_location:
            st.warning("장소명과 위치는 필수입니다.")
        else:
            lat, lng = st.session_state.selected_location
            st.session_state.itinerary.append({
                "name_ko": name_ko,
                "name_ja": name_ja,
                "start": start,
                "end": end,
                "note": note,
                "lat": lat,
                "lng": lng
            })
            st.session_state.selected_location = None
            st.success("일정 추가 완료")

# ===== 오른쪽 =====
with right:
    st.subheader("🗺️ 지도 (중심 선택 방식)")

    map_data = st_folium(
        build_map(
            itinerary=st.session_state.itinerary,
            selected_location=st.session_state.selected_location,
            center=st.session_state.map_center
        ),
        height=500,
        use_container_width=True
    )

    if map_data and map_data.get("center"):
        st.session_state.map_center = (
            map_data["center"]["lat"],
            map_data["center"]["lng"]
        )

    if st.button("📍 현재 화면 중심을 위치로 선택", use_container_width=True):
        st.session_state.selected_location = st.session_state.map_center
        st.success("위치 선택됨")

# -------------------------
# 전체 일정
# -------------------------
st.divider()
st.subheader("📋 전체 일정")

for idx, item in enumerate(st.session_state.itinerary):
    cols = st.columns([6, 1])
    with cols[0]:
        st.markdown(f"""
        **📍 {item['name_ko']}**  
        🕒 {item['start']} ~ {item['end']}  
        {item['note']}
        """)
    with cols[1]:
        if st.button("🗑", key=f"del_{idx}"):
            st.session_state.itinerary.pop(idx)
            st.rerun()

# -------------------------
# PDF 출력
# -------------------------
from pdf.pdf_generator import generate_pdf
import tempfile, os

st.divider()
st.subheader("📄 PDF 출력 (큰누나 인쇄용)")

if st.button("📥 PDF 생성"):
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "family_trip.pdf")
        generate_pdf(st.session_state.itinerary, None, pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 PDF 다운로드",
                f,
                file_name="가족여행일정.pdf",
                mime="application/pdf"
            )
