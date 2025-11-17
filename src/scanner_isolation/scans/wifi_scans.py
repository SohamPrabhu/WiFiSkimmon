# scans/wifi_scans.py
import platform
from datetime import datetime
import pywifi
from pywifi import const

def now_iso():
    return datetime.utcnow().isoformat()

# NEW — Normalize MAC/BSSID by removing trailing ":" only
def clean_mac(mac: str) -> str:
    if not mac:
        return ""
    return mac.rstrip(":").lower()

def scan_wifi():
    system = platform.system()

    if system == "Windows":
        return scan_wifi_windows()
    else:
        return {"error": "Only Windows"}


# ---------- WINDOWS ---------- #

def scan_wifi_windows():
    try:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        results = iface.scan_results()
    except Exception as e:
        return {"wifi_error": str(e)}

    wifi_data = []

    for n in results:
        mac_clean = clean_mac(n.bssid)

        wifi_data.append({
            "timestamp": now_iso(),
            "mac": mac_clean,
            "bssid": mac_clean,
            "ssid": n.ssid,
            "rssi": n.signal,
            "protocol": "WiFi",
            "model_score": None
        })

    return wifi_data
