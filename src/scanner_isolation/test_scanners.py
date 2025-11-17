import asyncio
import json
import requests
from datetime import datetime
from scans.wifi_scans import scan_wifi
from geo_location.location_service import get_device_location


INPUT_FILE = "scan_input.json"
OUTPUT_FILE = "scan_output.json"
url = "http://127.0.0.1:8000/api/detectwifi"

async def main():
    # Run WiFi scan
    wifi_results = scan_wifi()

    # Prepare data for location lookup
    wifi_for_location = []
    if isinstance(wifi_results, list):
        wifi_for_location = [
            {"bssid": ap["bssid"], "rssi": ap["rssi"]}
            for ap in wifi_results
        ]

    # Get location
    location = await get_device_location(wifi_for_location)

    # Final JSON structure
    input_data = {
        "wifi": wifi_results,
        "location": location
    }

    # Save input to file
    with open(INPUT_FILE, "w") as f:
        json.dump(input_data, f, indent=4)

    # Send to API
    response = requests.post(url, json=wifi_results)
    model_output = response.json()

    # Append location to the OUTPUT file
    output_data = {
        "model": model_output,
        "location": location
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
