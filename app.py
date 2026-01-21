import streamlit as st
from streamlit_folium import st_folium
from map.map_builder import build_map
from pdf.pdf_generator import generate_pdf
import tempfile, os

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="가족 여행 일정 지도",
    layout="wide"
)

st.title("🧳 가족 여행 일정 지도")
st.caption("왼쪽에서 일정 입력 → 오른쪽 지도에서 위치 지정 → 아래에서 일정 관리")

# -------------------------
# 세션 상태 초기화
# -------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = None
    st.session_state.selected_lng = None

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# -------------------------
# 상단 레이아웃
# -------------------------
left, right = st.columns([1, 2])

# =========================
# 왼쪽: 일정 입력 / 수정
# =========================
with left:
    st.subheader("✏️ 일정 입력 / 수정")

    # 수정 모드면 기존 값 로드
    if st.session_state.edit_index is not None:
        item = st.session_state.itinerary[st.session_state.edit_index]
        name_ko = st.text_input("장소명 (한글)", value=item["name_ko"])
        name_ja = st.text_input("장소명 (일본어, 선택)", value=item.get("name_ja", ""))
        start = st.text_input("시작 시간 (선택)", value=item.get("start", ""))
        end = st.text_input("종료 시간 (선택)", value=item.get("end", ""))
        note = st.text_area("메모 (선택)", value=item.get("note", ""), height=80)
        st.session_state.selected_lat = item["lat"]
        st.session_state.selected_lng = item["lng"]
    else:
        name_ko = st.text_input("장소명 (한글)")
        name_ja = st.text_input("장소명 (일본어, 선택)")
        start = st.text_input("시작 시간 (선택)")
        end = st.text_input("종료 시간 (선택)")
        note = st.text_area("메모 (선택)", height=80)

    st.markdown("### 📍 선택된 위치")
    if st.session_state.selected_lat:
        st.success(
            f"위도 {st.session_state.selected_lat:.5f}, "
            f"경도 {st.session_state.selected_lng:.5f}"
        )
    else:
        st.info("오른쪽 지도에서 위치를 지정하세요.")

    # 버튼 영역
    if st.session_state.edit_index is None:
        if st.button("📌 일정 추가", use_container_width=True):
            if not name_ko or not st.session_state.selected_lat:
                st.warning("장소명과 위치는 필수입니다.")
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
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 수정 저장", use_container_width=True):
                st.session_state.itinerary[st.session_state.edit_index] = {
                    "name_ko": name_ko,
                    "name_ja": name_ja,
                    "start": start,
                    "end": end,
                    "note": note,
                    "lat": st.session_state.selected_lat,
                    "lng": st.session_state.selected_lng
                }
                st.session_state.edit_index = None
                st.success("수정되었습니다.")
                st.rerun()
        with col2:
            if st.button("❌ 수정 취소", use_container_width=True):
                st.session_state.edit_index = None
                st.rerun()

# =========================
# 오른쪽: 지도
# =========================
with right:
    st.subheader("🗺️ 지도")
    map_data = st_folium(
        build_map(st.session_state.itinerary),
        height=500,
        use_container_width=True
    )

    if map_data and map_data.get("center"):
        if st.button("📍 현재 화면 중심을 위치로 선택", use_container_width=True):
            st.session_state.selected_lat = map_data["center"]["lat"]
            st.session_state.selected_lng = map_data["center"]["lng"]

# =========================
# 전체 일정 리스트
# =========================
st.divider()
st.subheader("📋 전체 일정")

if not st.session_state.itinerary:
    st.info("아직 등록된 일정이 없습니다.")
else:
    for i, item in enumerate(st.session_state.itinerary):
        cols = st.columns([6, 1, 1, 1, 1])
        with cols[0]:
            st.markdown(
                f"**📍 {item['name_ko']}** "
                f"{('(' + item['name_ja'] + ')') if item.get('name_ja') else ''}  \n"
                f"🕒 {item.get('start','')} ~ {item.get('end','')}  \n"
                f"{item.get('note','')}"
            )
        with cols[1]:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.rerun()
        with cols[2]:
            if st.button("▲", key=f"up_{i}") and i > 0:
                st.session_state.itinerary[i-1], st.session_state.itinerary[i] = \
                    st.session_state.itinerary[i], st.session_state.itinerary[i-1]
                st.rerun()
        with cols[3]:
            if st.button("▼", key=f"down_{i}") and i < len(st.session_state.itinerary)-1:
                st.session_state.itinerary[i+1], st.session_state.itinerary[i] = \
                    st.session_state.itinerary[i], st.session_state.itinerary[i+1]
                st.rerun()
        with cols[4]:
            if st.button("🗑", key=f"del_{i}"):
                st.session_state.itinerary.pop(i)
                st.rerun()

# =========================
# PDF 출력
# =========================
st.divider()
st.subheader("📄 PDF 출력 (큰누나 인쇄용)")

if st.button("📥 PDF 생성", use_container_width=True):
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "family_trip.pdf")
        generate_pdf(
            itinerary=st.session_state.itinerary,
            map_image_path=None,  # 지도 실패 대비
            output_path=pdf_path
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 PDF 다운로드",
                f,
                file_name="가족여행일정.pdf",
                mime="application/pdf"
            )
