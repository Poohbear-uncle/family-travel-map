import requests
from PIL import Image
from io import BytesIO

def generate_static_map(itinerary, output_path):
    if not itinerary:
        return

    center = f"{itinerary[0]['lat']},{itinerary[0]['lng']}"
    markers = "|".join([f"{i['lat']},{i['lng']}" for i in itinerary])

    url = "https://staticmap.openstreetmap.de/staticmap.php"
    params = {
        "center": center,
        "zoom": 11,
        "size": "800x500",
        "markers": markers
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        img = Image.open(BytesIO(r.content))
        img.save(output_path)
    except:
        pass
