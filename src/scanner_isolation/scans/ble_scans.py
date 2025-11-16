# scans/ble_scans.py
from datetime import datetime
from bleak import BleakScanner
import asyncio

def now_iso():
    return datetime.utcnow().isoformat()

async def _async_ble_scan():
    scanned = await BleakScanner.discover(timeout=5.0)
    devices = []

    for d in scanned:
        devices.append({
            "timestamp": now_iso(),
            "mac": d.address,
            "name": d.name,
            "bssid": None,
            "ssid": None,
            "rssi": d.rssi,
            "protocol": "BLE"
        })

    return devices


# ---------------------------------------------------------
# ✅ REPLACE YOUR OLD scan_ble() WITH THIS VERSION
# ---------------------------------------------------------
def scan_ble():
    """
    Safe BLE scan wrapper.
    If BLE fails or event loop exists → return empty list instead of error.
    """
    try:
        # Get / create event loop safely
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't run BLE inside an active loop (Windows/VSCode issue)
                return []
        except RuntimeError:
            # No loop exists, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(_async_ble_scan())

    except Exception:
        # BLE unsupported, permission error, radio locked, etc.
        return []
