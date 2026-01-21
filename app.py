import streamlit as st
from streamlit_folium import st_folium
import requests
import tempfile, os

from map.map_builder import build_map
from pdf.pdf_generator import generate_pdf

# =================================================
# 기본 설정
# =================================================
st.set_page_config(page_title="가족 여행 일정 지도", layout="wide")
st.title("🧳 가족 여행 일정 지도")
st.caption("왼쪽에서 일정 입력 · 오른쪽에서 검색 + 핀 드래그로 위치 지정")

# =================================================
# 세션 상태 초기화
# =================================================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = None
    st.session_state.selected_lng = None

if "temp_location" not in st.session_state:
    st.session_state.temp_location = None

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ✅ 기본 지도 중심 = 후쿠오카
if "map_center" not in st.session_state:
    st.session_state.map_center = (33.5902, 130.4017)

# =================================================
# 레이아웃
# =================================================
left, right = st.columns([1, 2])

# =================================================
# 왼쪽: 일정 입력 / 수정
# =================================================
with left:
    st.subheader("➕ 일정 입력 / ✏️ 수정")

    # 수정 모드일 때 기존 값 로드
    if st.session_state.edit_index is not None:
        item = st.session_state.itinerary[st.session_state.edit_index]
        default_name_ko = item["name_ko"]
        default_name_ja = item.get("name_ja", "")
        default_start = item.get("start", "")
        default_end = item.get("end", "")
        default_note = item.get("note", "")
    else:
        default_name_ko = ""
        default_name_ja = ""
        default_start = ""
        default_end = ""
        default_note = ""

    name_ko = st.text_input("장소명 (한글)", value=default_name_ko)
    name_ja = st.text_input("장소명 (일본어, 선택)", value=default_name_ja)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_time = st.text_input("시작 시간 (선택)", value=default_start)
    with col_t2:
        end_time = st.text_input("종료 시간 (선택)", value=default_end)

    note = st.text_area("메모 (선택)", value=default_note, height=80)

    if st.session_state.selected_lat:
        st.success(
            f"위도: {st.session_state.selected_lat:.5f}\n\n"
            f"경도: {st.session_state.selected_lng:.5f}"
        )
    else:
        st.info("오른쪽 지도에서 위치를 지정하세요.")

    # 버튼 분기
    if st.session_state.edit_index is None:
        if st.button("📌 일정 추가", use_container_width=True):
            if not name_ko or not st.session_state.selected_lat:
                st.warning("장소명과 위치는 필수입니다.")
            else:
                st.session_state.itinerary.append({
                    "name_ko": name_ko,
                    "name_ja": name_ja,
                    "start": start_time,
                    "end": end_time,
                    "note": note,
                    "lat": st.session_state.selected_lat,
                    "lng": st.session_state.selected_lng
                })
                st.session_state.selected_lat = None
                st.session_state.temp_location = None  # ✅ 임시 핀 제거
                st.success("일정이 추가되었습니다.")
                st.rerun()
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 수정 저장", use_container_width=True):
                i = st.session_state.edit_index
                st.session_state.itinerary[i].update({
                    "name_ko": name_ko,
                    "name_ja": name_ja,
                    "start": start_time,
                    "end": end_time,
                    "note": note,
                    "lat": st.session_state.selected_lat,
                    "lng": st.session_state.selected_lng
                })
                st.session_state.edit_index = None
                st.session_state.selected_lat = None
                st.session_state.temp_location = None  # ✅ 임시 핀 제거
                st.success("수정되었습니다.")
                st.rerun()
        with col2:
            if st.button("❌ 수정 취소", use_container_width=True):
                st.session_state.edit_index = None
                st.session_state.selected_lat = None
                st.session_state.temp_location = None
                st.rerun()

# =================================================
# 오른쪽: 🔍 검색 + 🖐 핀 드래그 지도
# =================================================
with right:
    st.subheader("🔍 장소 검색 & 위치 지정")

    query = st.text_input("장소 검색 (예: 후쿠오카 공항)")

    if query:
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "family-travel-map"}
        ).json()

        if res:
            lat, lng = float(res[0]["lat"]), float(res[0]["lon"])
            st.session_state.temp_location = (lat, lng)
            st.session_state.map_center = (lat, lng)
            st.info("검색 결과 위치에 임시 핀을 표시했습니다.")

    map_data = st_folium(
        build_map(
            itinerary=st.session_state.itinerary,
            temp_location=st.session_state.temp_location,
            center=st.session_state.map_center
        ),
        height=520,
        use_container_width=True
    )

    # 핀 클릭/드래그 결과 수신
    if map_data and map_data.get("last_object_clicked"):
        st.session_state.temp_location = (
            map_data["last_object_clicked"]["lat"],
            map_data["last_object_clicked"]["lng"]
        )

    if st.button("✅ 이 위치로 확정", use_container_width=True):
        if st.session_state.temp_location:
            st.session_state.selected_lat, st.session_state.selected_lng = \
                st.session_state.temp_location
            st.session_state.temp_location = None  # ✅ 빨간 핀 제거
            st.success("위치가 확정되었습니다.")

# =================================================
# 전체 일정 리스트
# =================================================
st.divider()
st.subheader("📋 전체 일정")

for i, item in enumerate(st.session_state.itinerary):
    cols = st.columns([6, 1, 1, 1, 1])
    time_text = ""
    if item.get("start") or item.get("end"):
        time_text = f"🕒 {item.get('start','')} ~ {item.get('end','')}"

    cols[0].markdown(
        f"**{i+1}. {item['name_ko']}**  \n{time_text}  \n{item.get('note','')}"
    )
    if cols[1].button("✏️", key=f"edit_{i}"):
        st.session_state.edit_index = i
        st.session_state.selected_lat = item["lat"]
        st.session_state.selected_lng = item["lng"]
        st.session_state.map_center = (item["lat"], item["lng"])
        st.rerun()
    if cols[2].button("▲", key=f"up_{i}") and i > 0:
        st.session_state.itinerary[i-1], st.session_state.itinerary[i] = \
            st.session_state.itinerary[i], st.session_state.itinerary[i-1]
        st.rerun()
    if cols[3].button("▼", key=f"down_{i}") and i < len(st.session_state.itinerary)-1:
        st.session_state.itinerary[i+1], st.session_state.itinerary[i] = \
            st.session_state.itinerary[i], st.session_state.itinerary[i+1]
        st.rerun()
    if cols[4].button("🗑", key=f"del_{i}"):
        st.session_state.itinerary.pop(i)
        st.rerun()

# =================================================
# PDF 출력
# =================================================
st.divider()
st.subheader("📄 PDF 출력 (큰누나 인쇄용)")

if st.button("📥 PDF 생성", use_container_width=True):
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
