import json
from pathlib import Path
from datetime import datetime, timezone
import folium, requests
from flask import Flask, jsonify, render_template, request, render_template_string

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parents[2]
SCAN_OUTPUT = BASE_DIR / "scan_output.json"
USER_REPORTS = []

def _read_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}

@app.route("/api/scan/input", methods=["GET"])
def scan_input_data():
    return jsonify(_read_json(BASE_DIR / "scan_input.json"))

@app.route("/api/scan/output", methods=["GET"])
def scan_output_data():
    return jsonify(_read_json(SCAN_OUTPUT))

@app.route("/api/geojson", methods=["GET"])
def geojson():
    data = []
    if SCAN_OUTPUT.exists():
        raw = json.loads(SCAN_OUTPUT.read_text())
        detections = raw.get("model", [])
        location = raw.get("location", {})
        lat = location.get("lat")
        lng = location.get("lon")
        for det in detections:
            feature = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "risk_level": det.get("risk_level", "low"),
                    "risk_score": det.get("risk_score", 0),
                    "source": "scan_output",
                    "reports": [det],
                    "last_seen_at": det.get("timestamp"),
                    "location_metadata": {"accuracy_m": None}
                }
            }
            data.append(feature)
    for rpt in USER_REPORTS:
        data.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [rpt["lng"], rpt["lat"]]},
            "properties": {
                "risk_level": rpt.get("risk_level", "user"),
                "risk_score": 1,
                "source": "user_report",
                "reports": [rpt],
                "last_seen_at": rpt["timestamp"],
                "location_metadata": {"accuracy_m": rpt.get("location_accuracy_m")}
            }
        })
    return jsonify({"type": "FeatureCollection", "features": data})

@app.route("/api/report", methods=["POST"])
def post_report():
    payload = request.get_json(force=True)
    entry = {
        "lat": float(payload["lat"]),
        "lng": float(payload["lng"]),
        "timestamp": payload.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "location_accuracy_m": payload.get("location_accuracy_m"),
        "evidence": payload.get("evidence"),
        "risk_level": payload.get("risk_level", "medium")
    }
    USER_REPORTS.append(entry)
    return jsonify({
        "status": "ok",
        "risk_level": entry["risk_level"],
        "received": entry
    })

@app.route("/report")
def report_form():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    return render_template("report.html", lat=lat, lng=lng)

@app.route("/map")
def map_page():
    lat = float(request.args.get("lat", 38.8340))
    lng = float(request.args.get("lng", -77.3056))

    m = folium.Map(location=[lat, lng], zoom_start=13, control_scale=True)
    gj = requests.get(request.url_root + "api/geojson").json()
    color_map = {"high": "red", "medium": "yellow", "low": "green"}
    for f in gj["features"]:
        props = f["properties"]
        coords = f["geometry"]["coordinates"]
        folium.Circle(
            location=[coords[1], coords[0]],
            radius=60 + 20 * int(props.get("risk_score", 0)),
            color=color_map.get(props.get("risk_level"), "green"),
            fill=True,
            fill_opacity=0.35,
            popup=f"Risk: {props.get('risk_level')} | Reports: {props.get('risk_score')} | "
                  f"Last seen: {props.get('last_seen_at')}"
        ).add_to(m)

    folium.GeoJson(gj, name="Skimmer Risk Cells").add_to(m)
    folium.LayerControl().add_to(m)

    html = m.get_root().render()
    custom_html = f"""
    <style>
      .map-controls {{
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }}
      .map-controls button {{
        background: #ff5722;
        color: white;
        border: none;
        border-radius: 18px;
        padding: 8px 14px;
        font-weight: bold;
        cursor: pointer;
      }}
      .map-controls button.locate {{
        background: #1E90FF;
      }}
    </style>
    <div class="map-controls">
      <button onclick="window.location.href='/report?lat={lat:.6f}&lng={lng:.6f}'">Report Here</button>
      <button class="locate" onclick="locateMe()">Locate Me</button>
    </div>
    <script>
      var locateMarker = null;
      function locateMe() {{
        if (!navigator.geolocation) return;
        navigator.geolocation.getCurrentPosition(function(pos) {{
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          var mapObj = null;
          for (var key in window) {{
            if (key.startsWith("map_")) {{ mapObj = window[key]; break; }}
          }}
          if (mapObj && window.L) {{
            if (locateMarker) {{
              mapObj.removeLayer(locateMarker);
            }}
            locateMarker = L.circleMarker([lat, lng], {{
              radius: 9,
              color: '#1E90FF',
              fillColor: '#1E90FF',
              fillOpacity: 0.9
            }}).addTo(mapObj);
            locateMarker.bindPopup("You are here").openPopup();
            mapObj.setView([lat, lng], 15);
          }} else {{
            window.location.href = `/map?lat=${{lat.toFixed(6)}}&lng=${{lng.toFixed(6)}}`;
          }}
        }});
      }}
    </script>
    """
    html = html.replace("</body>", custom_html + "</body>")
    return render_template_string(html)

# Only run the server if this file is executed directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
