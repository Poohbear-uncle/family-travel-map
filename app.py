import streamlit as st
from streamlit_folium import st_folium
import requests, tempfile, os
from supabase import create_client

from map.map_builder import build_map
from map.static_map import generate_static_map
from pdf.pdf_generator import generate_pdf

# ===============================
# Supabase 연결
# ===============================
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def load_itinerary():
    res = supabase.table("itinerary").select("*").order("order").execute()
    return res.data

def save_itinerary(data):
    supabase.table("itinerary").delete().neq("id", -1).execute()
    for i, item in enumerate(data):
        item["order"] = i
        supabase.table("itinerary").insert(item).execute()

# ===============================
# 기본 설정
# ===============================
st.set_page_config(page_title="가족 여행 일정 지도", layout="wide")
st.title("🧳 가족 여행 일정 지도")

# ===============================
# 세션 상태
# ===============================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = load_itinerary()

if "temp_location" not in st.session_state:
    st.session_state.temp_location = None

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = None
    st.session_state.selected_lng = None

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

map_center = (33.5902, 130.4017)  # 후쿠오카

left, right = st.columns([1, 2])

# ===============================
# 왼쪽: 일정 입력
# ===============================
with left:
    st.subheader("➕ 일정 입력 / ✏️ 수정")

    if st.session_state.edit_index is not None:
        item = st.session_state.itinerary[st.session_state.edit_index]
    else:
        item = {}

    name_ko = st.text_input("장소명 (한글)", item.get("name_ko",""))
    name_ja = st.text_input("장소명 (일본어)", item.get("name_ja",""))
    start = st.text_input("시작 시간", item.get("start",""))
    end = st.text_input("종료 시간", item.get("end",""))
    note = st.text_area("메모", item.get("note",""))

    if st.session_state.selected_lat:
        st.success(f"위도 {st.session_state.selected_lat:.5f}, 경도 {st.session_state.selected_lng:.5f}")

    if st.session_state.edit_index is None:
        if st.button("📌 일정 추가"):
            st.session_state.itinerary.append({
                "name_ko": name_ko,
                "name_ja": name_ja,
                "start": start,
                "end": end,
                "note": note,
                "lat": st.session_state.selected_lat,
                "lng": st.session_state.selected_lng
            })
            save_itinerary(st.session_state.itinerary)
            st.session_state.temp_location = None
            st.rerun()
    else:
        if st.button("💾 수정 저장"):
            st.session_state.itinerary[st.session_state.edit_index].update({
                "name_ko": name_ko,
                "name_ja": name_ja,
                "start": start,
                "end": end,
                "note": note,
                "lat": st.session_state.selected_lat,
                "lng": st.session_state.selected_lng
            })
            save_itinerary(st.session_state.itinerary)
            st.session_state.edit_index = None
            st.rerun()

# ===============================
# 오른쪽: 검색 + 핀 드래그
# ===============================
with right:
    st.subheader("🗺 지도 & 장소 검색")

    # -------------------------------
    # 장소 검색
    # -------------------------------
    query = st.text_input("🔍 장소 검색", key="search_query")

    if st.button("🔎 검색", key="search_button"):
        if not query.strip():
            st.warning("검색어를 입력하세요.")
        else:
            try:
                r = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": query,
                        "format": "json",
                        "limit": 1
                    },
                    headers={"User-Agent": "family-travel-map"}
                ).json()

                if r:
                    st.session_state.temp_location = (
                        float(r[0]["lat"]),
                        float(r[0]["lon"])
                    )
                else:
                    st.warning("검색 결과를 찾을 수 없습니다.")

            except Exception as e:
                st.error("검색 중 오류가 발생했습니다.")

    # -------------------------------
    # 지도 중심 결정
    # -------------------------------
    map_center_dynamic = (
        st.session_state.temp_location
        if st.session_state.temp_location
        else map_center
    )

    # -------------------------------
    # 지도 표시
    # -------------------------------
    map_data = st_folium(
        build_map(
            st.session_state.itinerary,
            st.session_state.temp_location,
            center=map_center_dynamic
        ),
        height=520,
        use_container_width=True
    )

    # -------------------------------
    # 지도 클릭 → 임시 위치 설정
    # -------------------------------
    if map_data and map_data.get("last_object_clicked"):
        st.session_state.temp_location = (
            map_data["last_object_clicked"]["lat"],
            map_data["last_object_clicked"]["lng"]
        )

    # -------------------------------
    # 위치 확정
    # -------------------------------
    if st.session_state.temp_location:
        st.info(
            f"선택된 위치: "
            f"{st.session_state.temp_location[0]:.5f}, "
            f"{st.session_state.temp_location[1]:.5f}"
        )

        if st.button("✅ 이 위치로 확정", key="confirm_location"):
            st.session_state.selected_lat, st.session_state.selected_lng = (
                st.session_state.temp_location
            )
            st.session_state.temp_location = None
            st.success("위치가 확정되었습니다.")
            st.rerun()


# ===============================
# 일정 리스트
# ===============================
st.divider()
for i, item in enumerate(st.session_state.itinerary):
    cols = st.columns([6,1,1,1,1])
    cols[0].markdown(f"**{i+1}. {item['name_ko']}**  \n{item.get('note','')}")
    if cols[1].button("✏️", key=f"e{i}"):
        st.session_state.edit_index = i
        st.session_state.selected_lat = item["lat"]
        st.session_state.selected_lng = item["lng"]
        st.rerun()
    if cols[2].button("▲", key=f"u{i}") and i>0:
        st.session_state.itinerary[i-1], st.session_state.itinerary[i] = st.session_state.itinerary[i], st.session_state.itinerary[i-1]
        save_itinerary(st.session_state.itinerary)
        st.rerun()
    if cols[3].button("▼", key=f"d{i}") and i<len(st.session_state.itinerary)-1:
        st.session_state.itinerary[i+1], st.session_state.itinerary[i] = st.session_state.itinerary[i], st.session_state.itinerary[i+1]
        save_itinerary(st.session_state.itinerary)
        st.rerun()
    if cols[4].button("🗑", key=f"x{i}"):
        st.session_state.itinerary.pop(i)
        save_itinerary(st.session_state.itinerary)
        st.rerun()

# ===============================
# PDF 출력
# ===============================
st.divider()
st.subheader("📄 PDF 출력 (큰누나 인쇄용)")

if st.button("📥 PDF 생성"):
    with tempfile.TemporaryDirectory() as tmp:
        map_img = os.path.join(tmp,"map.png")
        pdf_path = os.path.join(tmp,"family_trip.pdf")

        generate_static_map(st.session_state.itinerary, map_img)
        generate_pdf(st.session_state.itinerary, map_img, pdf_path)

        with open(pdf_path,"rb") as f:
            st.download_button("📄 PDF 다운로드", f, file_name="가족여행일정.pdf")
