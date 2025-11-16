# fake_skimmer.py
# Pico W - FreeWiFi with password 123456789 + fake HC-05 BLE beacon
# Works on every MicroPython version 2022-2025

import time
import network
import bluetooth
import struct

# ------------------- CONFIG -------------------
WIFI_SSID = "FreeWiFi"
WIFI_PASS = "123456789"       # common password people will guess instantly
BT_NAME   = "HC-05"           # shows up as real skimmer bluetooth module
# ----------------------------------------------

# proper BLE advertising data (shows in every scanner)
def make_adv_data(name):
    data = bytearray()
    def append(typ, value):
        nonlocal data
        data += struct.pack("BB", len(value) + 1, typ) + value
    append(0x01, b'\x06')               # Flags: General Discoverable + BLE only
    append(0x09, name.encode("utf-8"))  # Complete Local Name
    return data

# ------------------- START -------------------
print("\nStarting skimmer...")
print("WiFi :", WIFI_SSID)
print("Pass :", WIFI_PASS)
print("BLE  :", BT_NAME)

# WiFi AP - WPA2 with password 123456789
wlan = network.WLAN(network.AP_IF)
wlan.active(False)          # reset
time.sleep(0.1)
wlan.config(essid=WIFI_SSID)
wlan.config(password=WIFI_PASS)   # this makes it WPA2 + sets the password
wlan.active(True)
print("[+] WiFi AP active (WPA2)")

# BLE - fake HC-05
ble = bluetooth.BLE()
ble.active(True)

def advertise():
    ble.gap_advertise(100_000, adv_data=make_adv_data(BT_NAME), connectable=False)

advertise()
print("[+] BLE advertising as:", BT_NAME)

print("\n=== FULLY ACTIVE ===")
print("Waiting for connections... (Ctrl+C to stop)\n")

# keep BLE alive (some firmware stops after ~2 min)
try:
    while True:
        time.sleep(25)
        advertise()        # refresh advertisement
except KeyboardInterrupt:
    print("\nStopping everything...")
    ble.gap_advertise(None)
    wlan.active(False)
    print("All gone.")