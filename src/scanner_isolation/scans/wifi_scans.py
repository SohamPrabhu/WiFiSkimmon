# scans/wifi_scans.py
import platform
import subprocess
from datetime import datetime
import pywifi
from pywifi import const

def now_iso():
    return datetime.utcnow().isoformat()

def scan_wifi():
    system = platform.system()

    if system == "Windows":
        return scan_wifi_windows()
    elif system == "Darwin":
        return scan_wifi_macos()
    else:
        return {"error": "Only Windows + macOS supported."}


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
        wifi_data.append({
            "timestamp": now_iso(),
            "mac": n.bssid,
            "name": n.ssid,
            "bssid": n.bssid,
            "ssid": n.ssid,
            "rssi": n.signal,
            "protocol": "WiFi"
        })

    return wifi_data


# ---------- MACOS ---------- #

def scan_wifi_macos():
    wifi_data = []
    
    try:
        out = subprocess.check_output(
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
            text=True
        )
        lines = out.strip().split("\n")[1:]

        for line in lines:
            parts = line.split()
            ssid = parts[0]
            bssid = parts[1]
            rssi = int(parts[2])

            wifi_data.append({
                "timestamp": now_iso(),
                "mac": bssid,
                "name": ssid,
                "bssid": bssid,
                "ssid": ssid,
                "rssi": rssi,
                "protocol": "WiFi"
            })

    except Exception as e:
        return {"wifi_error": str(e)}

    return wifi_data
