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
    st.subheader("🗺️ 지도에서 위치 선택")

    map_data = st_folium(
        build_map(st.session_state.itinerary),
        height=500,
        use_container_width=True
    )

    if map_data and map_data.get("last_clicked"):
        st.session_state.selected_lat = map_data["last_clicked"]["lat"]
        st.session_state.selected_lng = map_data["last_clicked"]["lng"]

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

