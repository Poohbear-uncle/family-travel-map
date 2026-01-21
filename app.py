import streamlit as st
from streamlit_folium import st_folium
from map.map_builder import build_map

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="가족 여행 지도",
    layout="wide"
)

st.title("🧳 가족 여행 일정 지도")
st.caption("지도 클릭으로 위치를 지정하고, 일정은 실수해도 안전하게 수정/삭제할 수 있습니다.")

# ---------------------------
# 세션 상태 초기화
# ---------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "delete_index" not in st.session_state:
    st.session_state.delete_index = None

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = None

if "selected_lng" not in st.session_state:
    st.session_state.selected_lng = None

# ---------------------------
# 일정 추가 폼
# ---------------------------
st.subheader("➕ 일정 추가")

with st.form("add_schedule", clear_on_submit=True):
    name_ko = st.text_input("장소명 (한글)")
    name_ja = st.text_input("장소명 (일본어, 선택)")
    col1, col2 = st.columns(2)
    with col1:
        start = st.text_input("시작 시간 (선택)")
    with col2:
        end = st.text_input("종료 시간 (선택)")
    note = st.text_area("메모 (선택)")

    lat = st.session_state.selected_lat
    lng = st.session_state.selected_lng

    submitted = st.form_submit_button("📌 일정 추가")

    if submitted:
        if not name_ko:
            st.warning("장소명(한글)은 필수입니다.")
        elif lat is None or lng is None:
            st.warning("지도를 클릭하여 위치를 먼저 선택해주세요.")
        else:
            st.session_state.itinerary.append({
                "name_ko": name_ko,
                "name_ja": name_ja,
                "start": start,
                "end": end,
                "note": note,
                "lat": lat,
                "lng": lng
            })
            st.success("일정이 추가되었습니다.")
            st.session_state.selected_lat = None
            st.session_state.selected_lng = None

st.divider()

# ---------------------------
# 지도 영역 (오른쪽)
# ---------------------------
st.subheader("🗺️ 지도에서 위치 선택")

map_data = st_folium(
    build_map(st.session_state.itinerary),
    height=450,
    use_container_width=True
)

if map_data and map_data.get("last_clicked"):
    st.session_state.selected_lat = map_data["last_clicked"]["lat"]
    st.session_state.selected_lng = map_data["last_clicked"]["lng"]
    st.success(
        f"📍 위치 선택됨: "
        f"{st.session_state.selected_lat:.5f}, "
        f"{st.session_state.selected_lng:.5f}"
    )

st.divider()

# ---------------------------
# 일정 카드 표시
# ---------------------------
st.subheader("📋 전체 일정")

def render_card(item, index):
    with st.container():
        st.markdown(
            f"""
            <div style="
                border:1px solid #ddd;
                border-radius:14px;
                padding:20px;
                margin-bottom:18px;
                background-color:#f9f9f9;
            ">
            <h4>📍 {item['name_ko']} <small>({item.get('name_ja','')})</small></h4>
            <p>🕒 {item.get('start','')} ~ {item.get('end','')}</p>
            <p>{item.get('note','')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 수정", key=f"edit_{index}"):
                st.session_state.edit_index = index

        with col2:
            if st.button("🗑 삭제", key=f"delete_{index}"):
                st.session_state.delete_index = index

# 카드 렌더링
for idx, item in enumerate(st.session_state.itinerary):
    render_card(item, idx)

# ---------------------------
# 수정 모드
# ---------------------------
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    item = st.session_state.itinerary[idx]

    st.subheader("✏️ 일정 수정")

    name_ko = st.text_input("장소명 (한글)", item["name_ko"])
    name_ja = st.text_input("장소명 (일본어, 선택)", item.get("name_ja", ""))

    col1, col2 = st.columns(2)
    with col1:
        start = st.text_input("시작 시간", item.get("start", ""))
    with col2:
        end = st.text_input("종료 시간", item.get("end", ""))

    note = st.text_area("메모", item.get("note", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 저장"):
            st.session_state.itinerary[idx].update({
                "name_ko": name_ko,
                "name_ja": name_ja,
                "start": start,
                "end": end,
                "note": note
            })
            st.session_state.edit_index = None
            st.success("수정되었습니다.")

    with col2:
        if st.button("❌ 취소"):
            st.session_state.edit_index = None

# ---------------------------
# 삭제 확인 모드
# ---------------------------
if st.session_state.delete_index is not None:
    idx = st.session_state.delete_index

    st.warning("⚠️ 이 일정을 정말 삭제할까요?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ 취소"):
            st.session_state.delete_index = None

    with col2:
        if st.button("🗑 삭제 확정"):
            del st.session_state.itinerary[idx]
            st.session_state.delete_index = None
            st.success("일정이 삭제되었습니다.")
