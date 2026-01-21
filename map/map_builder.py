import folium

def build_map(itinerary, temp_location=None, center=(35.68, 139.76)):
    """
    itinerary: 확정된 일정 리스트
    temp_location: (lat, lng) 임시 위치 (검색 / 드래그 중)
    center: 지도 중심
    """

    m = folium.Map(location=center, zoom_start=12)

    # ✅ 확정된 일정 핀
    for item in itinerary:
        folium.Marker(
            location=[item["lat"], item["lng"]],
            icon=folium.Icon(color="blue"),
            tooltip=folium.Tooltip(
                f"""
                <div style="
                    max-width:240px;
                    padding:10px;
                    border-radius:14px;
                    background:#f8f8f8;
                    font-size:13px;
                    line-height:1.5;
                ">
                    <b>{item['name_ko']}</b><br/>
                    {item.get('name_ja','')}<br/>
                    {item.get('note','')}
                </div>
                """,
                sticky=True
            )
        ).add_to(m)

    # 🔴 임시 핀 (검색 / 드래그용)
    if temp_location:
        folium.Marker(
            location=temp_location,
            draggable=True,
            icon=folium.Icon(color="red"),
            tooltip="📍 드래그해서 위치를 미세 조정하세요"
        ).add_to(m)

    return m
