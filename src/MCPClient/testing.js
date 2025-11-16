async function scanBluetooth() {
  const data = {
    device_id: "pump_42",
    rssi: -45,
    device_name: "HC-05",
    mac_address: "00:14:03:06:12:34",
    timestamp: new Date().toISOString(),
    location: {
      latitude: 38.8462,
      longitude: -77.3064
    }
  };
  const response = await fetch('http://localhost:8000/api/detectbluetooth', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  console.log(result)
}
