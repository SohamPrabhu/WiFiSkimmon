# run_scans.py
from scans.ble_scans import scan_ble
from scans.wifi_scans import scan_wifi
from geo_location.location_service import get_device_location

def run_scans_and_locate():
    results = {}

    # BLE Scan
    ble_results = scan_ble()

    # WiFi Scan
    wifi_results = scan_wifi()

    # Shared MLS location (WiFi only)
    location = get_device_location(
        wifi_results if isinstance(wifi_results, list) else []
    )

    results["ble"] = ble_results
    results["wifi"] = wifi_results
    results["location"] = location

    return results
