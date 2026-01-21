import folium
from folium.plugins import MarkerCluster

def build_map(
    itinerary,
    temp_location=None,
    center=(33.5902, 130.4017),
    zoom=7
):

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="cartodbpositron"
    )

    cluster = MarkerCluster().add_to(m)

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
            <b>📍 {item['name_ko']}</b><br>
            {item.get('start','')} ~ {item.get('end','')}<br>
            {item.get('note','')}
        </div>
        """
        folium.Marker(
            [item["lat"], item["lng"]],
            popup=popup_html,
            tooltip=item["name_ko"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(cluster)

    # 🟠 드래그 가능한 임시 핀
    if temp_location:
        folium.Marker(
            temp_location,
            draggable=True,
            tooltip="핀을 드래그하여 위치를 미세 조정하세요",
            icon=folium.Icon(color="orange", icon="star")
        ).add_to(m)


    return m
