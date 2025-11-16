# geo_location/location_service.py

import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read API key
GOOGLE_API_KEY = os.getenv("GOOGLE_GEO_API_KEY")

GOOGLE_GEO_URL = (
    "https://www.googleapis.com/geolocation/v1/geolocate?key={}"
)


async def get_device_location(wifi_list):
    """
    Get an approximate lat/lon using Google Geolocation API.
    wifi_list should be:
    [
        {"bssid": "...", "rssi": -55}
    ]
    """

    # No key = no location
    if not GOOGLE_API_KEY:
        print("GOOGLE_GEO_API_KEY missing!")
        return {"lat": None, "lon": None}

    # No WiFi scanned = no location
    if not wifi_list:
        return {"lat": None, "lon": None}

    # Sort and limit to top 3 access points
    wifi_sorted = sorted(wifi_list, key=lambda x: x["rssi"], reverse=True)
    wifi_top3 = wifi_sorted[:3]

    # Build minimal payload
    payload = {
        "wifiAccessPoints": [
            {"macAddress": ap["bssid"], "signalStrength": ap["rssi"]}
            for ap in wifi_top3
        ]
    }

    try:
        response = requests.post(
            GOOGLE_GEO_URL.format(GOOGLE_API_KEY),
            json=payload,
            timeout=4
        )

        # API error (invalid key, quota exhausted, etc)
        if response.status_code != 200:
            print("Google API error:", response.text)
            return {"lat": None, "lon": None}

        data = response.json()

        # Expected response:
        # {
        #   "location": { "lat": ..., "lng": ... },
        #   "accuracy": 100
        # }
        if "location" in data:
            return {
                "lat": data["location"]["lat"],
                "lon": data["location"]["lng"]
            }

    except Exception as e:
        print("Location lookup exception:", e)

    # fallback
    return {"lat": None, "lon": None}
