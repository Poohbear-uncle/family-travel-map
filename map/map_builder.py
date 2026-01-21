import folium

COLOR_BY_DAY = [
    "#6B8E9E", "#8FAE8E", "#C2A27E", "#A890B5"
]

def format_place_name(e):
    if e.get("title_ja"):
        return f"{e['title_ko']} ({e['title_ja']})"
    return e["title_ko"]

def build_map(schedule):
    if not schedule:
        return folium.Map(location=[33.5, 130.5], zoom_start=7)

    avg_lat = sum(e["lat"] for e in schedule) / len(schedule)
    avg_lon = sum(e["lon"] for e in schedule) / len(schedule)

    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=7,
        tiles="cartodbpositron"
    )

    for e in schedule:
        color = COLOR_BY_DAY[(e["day"] - 1) % len(COLOR_BY_DAY)]

        popup_text = f"""
        <b>{format_place_name(e)}</b><br>
        {e.get('memo','')}
        """

        folium.CircleMarker(
            location=[e["lat"], e["lon"]],
            radius=9 if e["type"] == "숙소" else 6,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=popup_text
        ).add_to(m)

    return m
