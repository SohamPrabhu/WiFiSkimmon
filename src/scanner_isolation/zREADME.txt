Required pip installs:
pip install pywifi pybluez pyserial requests

What’s implemented now:
WiFi scanning (RSSI, BSSID) using pywifi
BLE scanning using PyBluez
NFC scanning over serial using pyserial
All signals normalized into a shared JSON structure
Strongest WiFi signals sent to Google Geolocation API
API returns estimated latitude/longitude

Not implemented yet:
ChatGPT anomaly detection (needs openai package)
Isolation Forest ML anomaly detector (needs scikit-learn)

How it works:
WiFi, BLE, and NFC scanners collect real environmental signals.
Each result is converted into a JSON entry with:
timestamp, mac, protocol, rssi, name/bssid/ssid (if available)
WiFi signals are formatted into Google’s wifiAccessPoints payload.
The script sends the request to Google Geolocation API.

API returns { location: { lat, lng }, accuracy }.

JSON format (internal signals):

{
  "timestamp": "2025-11-01T10:32:22Z",
  "mac": "00:11:22:33:44:55",
  "protocol": "WiFi",
  "rssi": -64,
  "name": null,
  "bssid": "00:11:22:33:44:55",
  "ssid": null
}


Google Geolocation payload:

{
  "wifiAccessPoints": [
    {
      "macAddress": "00:11:22:33:44:55",
      "signalStrength": -61,
      "age": 0
    }
  ]
}


Google response:

{
  "location": { "lat": 37.4219, "lng": -122.084 },
  "accuracy": 65
}


Run the program:
python main.py


Set your API key:
export GOOGLE_GEO_API_KEY="YOUR_KEY_HERE"