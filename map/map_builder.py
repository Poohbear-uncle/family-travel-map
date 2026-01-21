import folium

COLOR_BY_DAY = [
    "#6B8E9E", "#8FAE8E", "#C2A27E", "#A890B5"
]

def build_map(schedule):
    m = folium.Map(
        location=[33.5, 130.5],
        zoom_start=8,
        tiles="cartodbpositron"  # 저채도
    )

    for e in schedule:
        color = COLOR_BY_DAY[(e["day"] - 1) % len(COLOR_BY_DAY)]
        popup_text = f"""
        <b>{e['title_ko']}</b><br>
        {e['title_ja']}<br>
        {e.get('memo', '')}
        """

        folium.CircleMarker(
            location=[e["lat"], e["lon"]],
            radius=8 if e["type"] == "숙소" else 5,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=popup_text
        ).add_to(m)

    return m
