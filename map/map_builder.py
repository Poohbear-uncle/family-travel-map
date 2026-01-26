import folium


def build_map(itinerary, temp_location=None, center=(0, 0)):
    """
    itinerary: [
        {
            "name_ko": str,
            "name_ja": str,
            "start": str,
            "end": str,
            "note": str,
            "lat": float | None,
            "lng": float | None
        },
        ...
    ]
    temp_location: (lat, lng) | None
    center: (lat, lng)
    """

    # 지도 생성
    m = folium.Map(
        location=center,
        zoom_start=12,
        control_scale=True
    )

    # ===============================
    # 일정 마커
    # ===============================
    for idx, item in enumerate(itinerary):
        lat = item.get("lat")
        lng = item.get("lng")

        # 🔴 좌표 없으면 스킵 (ValueError 방지)
        if lat is None or lng is None:
            continue

        popup_html = f"""
        <b>{idx + 1}. {item.get("name_ko", "")}</b><br>
        {item.get("name_ja", "")}<br>
        {item.get("start", "")} ~ {item.get("end", "")}<br>
        {item.get("note", "")}
        """

        folium.Marker(
            location=[lat, lng],
            popup=popup_html,
            tooltip=item.get("name_ko", ""),
            icon=folium.Icon(color="blue", icon="map-marker")
        ).add_to(m)

    # ===============================
    # 임시 위치 마커 (검색 / 클릭)
    # ===============================
    if temp_location is not None:
        temp_lat, temp_lng = temp_location

        # 안전 체크
        if temp_lat is not None and temp_lng is not None:
            folium.Marker(
                location=[temp_lat, temp_lng],
                tooltip="선택 중인 위치",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

    return m
