import folium

def build_map(itinerary, center=(33.5902, 130.4017), zoom=9):
    """
    itinerary: 일정 리스트
    """
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB positron"  # 저채도, 인쇄 친화
    )

    for item in itinerary:
        folium.Marker(
            location=[item["lat"], item["lng"]],
            popup=f"{item['name_ko']} ({item.get('name_ja','')})",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    return m
