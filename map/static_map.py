import requests

def generate_static_map(itinerary, output_path):
    if not itinerary:
        return None

    base_url = "https://staticmap.openstreetmap.de/staticmap.php"

    markers = []
    for item in itinerary:
        markers.append(f"{item['lat']},{item['lng']},blue-pushpin")

    params = {
        "size": "900x600",
        "maptype": "mapnik",
        "markers": "|".join(markers)
    }

    try:
        res = requests.get(base_url, params=params, timeout=10)
        res.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(res.content)

        return output_path

    except Exception as e:
        # 🚑 Cloud 환경에서 매우 중요
        print("⚠️ 정적 지도 생성 실패:", e)
        return None
