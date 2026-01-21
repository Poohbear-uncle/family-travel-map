import streamlit as st
from streamlit_folium import st_folium
from map.map_builder import build_map

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="가족 여행 일정 지도",
    layout="wide"
)

st.title("🧳 가족 여행 일정 지도")
st.caption("왼쪽에서 일정 입력 → 오른쪽 지도에서 위치 선택 → 아래에서 전체 일정 확인")

# -------------------------
# 세션 상태 초기화
# -------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = None

if "selected_lng" not in st.session_state:
    st.session_state.selected_lng = None

# -------------------------
# 상단: 입력 / 지도 (좌우 분리)
# -------------------------
left, right = st.columns([1, 2])

# ===== 왼쪽: 일정 입력 =====
with left:
    st.subheader("➕ 일정 입력")

    name_ko = st.text_input("장소명 (한글)")
    name_ja = st.text_input("장소명 (일본어, 선택)")

    col1, col2 = st.columns(2)
    with col1:
        start = st.text_input("시작 시간 (선택)")
    with col2:
        end = st.text_input("종료 시간 (선택)")

    note = st.text_area("메모 (선택)", height=80)

    st.markdown("### 📍 선택된 위치")
    if st.session_state.selected_lat is not None:
        st.success(
            f"위도: {st.session_state.selected_lat:.5f}\n\n"
            f"경도: {st.session_state.selected_lng:.5f}"
        )
    else:
        st.info("오른쪽 지도에서 위치를 클릭하세요.")

    if st.button("📌 일정 추가", use_container_width=True):
        if not name_ko:
            st.warning("장소명(한글)은 필수입니다.")
        elif st.session_state.selected_lat is None:
            st.warning("지도에서 위치를 먼저 선택하세요.")
        else:
            st.session_state.itinerary.append({
                "name_ko": name_ko,
                "name_ja": name_ja,
                "start": start,
                "end": end,
                "note": note,
                "lat": st.session_state.selected_lat,
                "lng": st.session_state.selected_lng
            })
            st.session_state.selected_lat = None
            st.session_state.selected_lng = None
            st.success("일정이 추가되었습니다.")

# ===== 오른쪽: 지도 =====
with right:
    st.subheader("🗺️ 지도에서 위치 지정")

    st.caption("지도를 움직여 원하는 장소를 화면 가운데에 둔 뒤 버튼을 누르세요.")

    map_data = st_folium(
        build_map(st.session_state.itinerary),
        height=500,
        use_container_width=True
    )

    if map_data and map_data.get("center"):
        center_lat = map_data["center"]["lat"]
        center_lng = map_data["center"]["lng"]

        if st.button("📍 현재 화면 중심을 위치로 선택", use_container_width=True):
            st.session_state.selected_lat = center_lat
            st.session_state.selected_lng = center_lng


# -------------------------
# 전체 일정 (리스트형)
# -------------------------
st.divider()
st.subheader("📋 전체 일정")

if not st.session_state.itinerary:
    st.info("아직 등록된 일정이 없습니다.")
else:
    for idx, item in enumerate(st.session_state.itinerary):
        row = st.columns([6, 1])
        with row[0]:
            st.markdown(
                f"""
                **📍 {item['name_ko']}** {f"({item['name_ja']})" if item['name_ja'] else ""}  
                🕒 {item.get('start','')} ~ {item.get('end','')}  
                {item.get('note','')}
                """
            )
        with row[1]:
            if st.button("🗑", key=f"delete_{idx}"):
                st.session_state.itinerary.pop(idx)
                st.rerun()

# =========================
# PDF 출력 (항상 하단)
# =========================
st.divider()
st.subheader("📄 PDF 출력")
st.caption("큰누나용 인쇄 파일 (A4, 2페이지)")

try:
    from pdf.pdf_generator import generate_pdf
    import tempfile
    import os

    if st.button("📥 PDF로 저장하기", use_container_width=True):
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "family_trip.pdf")

            generate_pdf(
                itinerary=st.session_state.itinerary,
                map_image_path=None,
                output_path=pdf_path
            )

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 PDF 다운로드",
                    data=f,
                    file_name="가족여행일정.pdf",
                    mime="application/pdf"
                )

except Exception as e:
    st.error("❌ PDF 모듈 로딩 실패")
    st.code(str(e))
