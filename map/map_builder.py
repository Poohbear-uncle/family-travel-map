import folium

def build_map(
    itinerary,
    selected_location=None,
    center=(33.5902, 130.4017),
    zoom=7
):
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="cartodbpositron"
    )

    # ✅ 확정 일정 핀
    for item in itinerary:
        popup_html = f"""
        <div style="
            max-width:260px;
            padding:10px;
            border-radius:14px;
            background:#ffffff;
            box-shadow:0 2px 8px rgba(0,0,0,0.15);
            font-size:14px;
            line-height:1.5;
        ">
            <b style="font-size:15px;">📍 {item['name_ko']}</b><br>
            <span style="color:#666;">
                {item.get('start','')} ~ {item.get('end','')}
            </span><br>
            <div style="margin-top:6px;">
                {item.get('note','')}
            </div>
        </div>
        """

        folium.Marker(
            [item["lat"], item["lng"]],
            popup=popup_html,
            tooltip=item["name_ko"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # 🟠 임시 선택 핀
    if selected_location:
        folium.Marker(
            selected_location,
            tooltip="선택된 위치",
            icon=folium.Icon(color="orange", icon="star")
        ).add_to(m)

    # ➕ 중심 십자
    folium.Marker(
        center,
        icon=folium.DivIcon(
            html="""
            <div style="
                font-size:28px;
                color:#ff4b4b;
                font-weight:bold;
                transform: translate(-50%, -50%);
            ">+</div>
            """
        )
    ).add_to(m)

    return m
