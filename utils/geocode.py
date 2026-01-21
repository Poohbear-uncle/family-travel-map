import requests

def geocode_place(query: str):
    """
    Nominatim(OpenStreetMap) 기반 장소 검색
    """
    if not query:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "family-travel-map"
    }

    res = requests.get(url, params=params, headers=headers, timeout=10)
    if res.status_code != 200:
        return None

    data = res.json()
    if not data:
        return None

    return float(data[0]["lat"]), float(data[0]["lon"])
