import streamlit as st
from streamlit_folium import st_folium
from map.map_builder import build_map
from utils.geocode import geocode_place

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(page_title="가족 여행 일정 지도", layout="wide")
st.title("🧳 가족 여행 일정 지도")
st.caption("검색 → 핀 드래그 → 위치 확정 → 일정 추가")

# -------------------------
# 세션 상태 초기화
# -------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "map_center" not in st.session_state:
    st.session_state.map_center = (33.5902, 130.4017)

if "temp_location" not in st.session_state:
    st.session_state.temp_location = None

if "selected_location" not in st.session_state:
    st.session_state.selected_location = None

# -------------------------
# 레이아웃
# -------------------------
left, right = st.columns([1, 2])

# =========================
# 왼쪽: 일정 입력
# =========================
with left:
    st.subheader("➕ 일정 입력")

    # 🔍 장소 검색
    search_query = st.text_input(
        "🔍 장소 검색 (한글 / 일본어)",
        placeholder="예: 후쿠오카 공항, 糸島, 雷山千如寺"
    )

    if st.button("📡 검색 후 임시 핀 생성", use_container_width=True):
        result = geocode_place(search_query)
        if result:
            st.session_state.temp_location = result
            st.session_state.map_center = result
            st.session_state.selected_location = None
            st.success("임시 핀이 생성되었습니다. 핀을 드래그해 주세요.")
        else:
            st.warning("검색 결과를 찾을 수 없습니다.")

    st.divider()

    name_ko = st.text_input("장소명 (한글)")
    name_ja = st.text_input("장소명 (일본어, 선택)")
    start = st.text_input("시작 시간 (선택)")
    end = st.text_input("종료 시간 (선택)")
    note = st.text_area("메모", height=80)

    st.markdown("### 📍 현재 선택된 위치")
    if st.session_state.selected_location:
        lat, lng = st.session_state.selected_location
        st.success(f"위도 {lat:.5f}, 경도 {lng:.5f}")
    else:
        st.info("오른쪽 지도에서 핀을 드래그한 후 위치를 확정하세요.")

    if st.button("📌 일정 추가", use_container_width=True):
        if not name_ko:
            st.warning("장소명(한글)은 필수입니다.")
        elif not st.session_state.selected_location:
            st.warning("위치를 먼저 확정하세요.")
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
            st.session_state.temp_location = None
            st.success("일정이 추가되었습니다.")

# =========================
# 오른쪽: 지도
# =========================
with right:
    st.subheader("🗺️ 지도 (핀 드래그 방식)")

    map_data = st_folium(
        build_map(
            itinerary=st.session_state.itinerary,
            temp_location=st.session_state.temp_location,
            center=st.session_state.map_center
        ),
        height=520,
        use_container_width=True
    )

    # ✅ 핀 드래그 후 좌표 수신
    if map_data and map_data.get("last_object_clicked"):
        lat = map_data["last_object_clicked"]["lat"]
        lng = map_data["last_object_clicked"]["lng"]
        st.session_state.temp_location = (lat, lng)

    # 📌 위치 확정
    if st.button("📍 이 위치로 확정", use_container_width=True):
        if st.session_state.temp_location:
            st.session_state.selected_location = st.session_state.temp_location
            st.success("위치가 확정되었습니다.")
        else:
            st.warning("먼저 임시 핀을 생성하세요.")

# =========================
# 전체 일정
# =========================
st.divider()
st.subheader("📋 전체 일정")

if not st.session_state.itinerary:
    st.info("아직 등록된 일정이 없습니다.")
else:
    for idx, item in enumerate(st.session_state.itinerary):
        cols = st.columns([6, 1])
        with cols[0]:
            st.markdown(f"""
            **📍 {item['name_ko']}** {f"({item['name_ja']})" if item['name_ja'] else ""}  
            🕒 {item['start']} ~ {item['end']}  
            {item['note']}
            """)
        with cols[1]:
            if st.button("🗑", key=f"del_{idx}"):
                st.session_state.itinerary.pop(idx)
                st.rerun()
