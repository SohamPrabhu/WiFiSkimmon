# test_scanners.py

import asyncio
import json

from scans.ble_scans import scan_ble
from scans.wifi_scans import scan_wifi
from geo_location.location_service import get_device_location


async def main():
    print("=== Running BLE Scan ===")
    ble_results = scan_ble()
    print(f"BLE found {len(ble_results) if isinstance(ble_results, list) else 0} devices")

    print("\n=== Running WiFi Scan ===")
    wifi_results = scan_wifi()
    if isinstance(wifi_results, list):
        print(f"WiFi found {len(wifi_results)} networks")
    else:
        print("WiFi scan error:", wifi_results)

    print("\n=== Running Location Lookup ===")
    # send ONLY real WiFi access points
    wifi_for_location = []
    if isinstance(wifi_results, list):
        for ap in wifi_results:
            wifi_for_location.append({
                "bssid": ap["bssid"],
                "rssi": ap["rssi"]
            })

    location = await get_device_location(wifi_for_location)

    output = {
        "ble": ble_results,
        "wifi": wifi_results,
        "location": location
    }

    print("\n=== FINAL OUTPUT ===")
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
