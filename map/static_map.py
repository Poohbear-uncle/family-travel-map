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

    res = requests.get(base_url, params=params, timeout=15)
    if res.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(res.content)
        return output_path

    return None
