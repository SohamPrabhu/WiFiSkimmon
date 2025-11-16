# Skimmon
A crowd-controlled system used to find skimmers in local areas to increase safety with money.

## Overview
Skimmon uses AI detection to find suspected skimmer devices at ATMs, gas pumps, and point-of-sale terminals. Reports are then added to a live updated map seen by every party using the software. This helps the community avoid fraud and raises awareness of unsafe locations.

## Features
- Interactive map (Folium + Flask, GeoJSON)
- Wi-Fi detection of skimmers using AI to identify suspicious signals
- Multi-user visibility
- Firebase Firestore + SQLite integration
- Wi-Fi scanning to find skimming devices in the area
- MCP server integration for modular expansion

## Technical Architecture
- **Frontend:** Flask templates + Folium map rendering  
- **Backend:** Python Flask server, Firestore integration, SQLite caching  
- **Data Standards:** GeoJSON for location-based reporting  
- **MCP Server:** FastAPI-based detection workflow 
## MCP Server (`main.py`)

Skimmon includes a FastAPI-based MCP server (`main.py`) that powers the Wi‑Fi detection workflow. It connects raw Wi‑Fi scan data to AI analysis and returns risk assessments that are displayed on the crowdsourced map.

### Key Responsibilities
- **Wi‑Fi Scan Input Models:** Defines structured inputs (`WifiScanInput`) with fields like MAC, BSSID, SSID, RSSI, and protocol.
- **Risk Assessment:** Uses OpenAI (`gpt‑4o‑mini`) with custom prompts and tools to analyze suspicious Wi‑Fi signals.
- **Risk Levels:** Classifies devices into `low`, `medium`, or `high` risk based on AI scoring.
- **Local Storage:** Keeps a record of all detections in memory (`all_detections`).
- **API Endpoints:**
  - `GET /health` → Health check for server status.
  - `POST /api/detectwifi` → Accepts Wi‑Fi scan data, returns risk assessments with AI comments.
  - `GET /api/detections` → Lists all stored detections.
  - `GET /api/risk-analysis/{detection_id}` → Retrieves detailed analysis for a specific detection.

### Example Workflow
1. Client submits Wi‑Fi scans → `POST /api/detectwifi`
2. MCP server calls AI model → Generates risk scores + explanations
3. Server stores detection → Adds to `all_detections`
4. Results returned → Risk level + AI comments displayed on Skimmon map

### Running the MCP Server
To run the MCP server locally:
```bash
cd mcp_server
uvicorn main:app --reload
```
## Wi-Fi Detection system
Skimmon  uses Wi‑Fi scanning as its primary method for detecting suspicious devices that may be skimmers. The detection system is composed of several modules: 
**(`scans/wifi_scans.py`)**
- Performs raw Wi‑Fi scans using PyWiFi (Windows only).
- Returns structured data including BSSID, SSID, RSSI, and timestamp.

**(`run_scans.py`)**
- Provides a reusable function ('run_scans_and_locate()') that integrates Wi‑Fi scanning and location lookup.
- Returns a dictionary containing both raw Wi‑Fi results and location data.

 **(`test_scanners.py`)**
- Demo script that runs a Wi‑Fi scan and location lookup.
- Outputs results in JSON format for testing.
  ### Entry point Script
-Imports (`run_scans_ans_locate()') and prints results directly
-Provides a simple way to run the full detection pipeline end-to-end

## Fake Skimmer Test 
To validate Skimmon’s detection pipeline, we built a simulated skimmer device using a Raspberry Pi Pico W running MicroPython. This test script safely mimics the behavior of real skimmers without using malicious hardware.

- **Wi‑Fi Simulation:** Broadcasts a weak WPA2 access point named FreeWiFi with a common password (123456789).
- **BLE Simulation:** Advertises as HC‑05, a Bluetooth module often found in skimmer devices.
- Persistence: Keeps both Wi‑Fi and BLE signals active, refreshing advertisements to ensure they show up in scans.
### Why It Matters
- Provides a controlled, ethical test environment for Skimmon.
- Confirms that the detection pipeline correctly flags suspicious SSIDs and BLE beacons.
- Demonstrates end‑to‑end validation: simulated signals → MCP server → AI risk scoring → crowdsourced map visualization.

## Deployment Goals:
  - Have an iOS and Android app to use this system wherever you go.  
  - Be able to use BLE to detect these devices as well (due to hardware restrictions we could not implement this now).  

## Usage
1. Open the map on localhost or hosted domain  
2. Explore the map of reported risks  
3. Run the Wi-Fi scan to detect suspicious signals  
4. Get an automated report and risk score from AI  
5. See updates appear on the map  

## Pitch
- **Problem:** Card skimmers cost consumers millions annually, and consumers don’t have an easy way of preventing it.  
- **Solution:** Skimmon uses Wi-Fi scanning to detect suspicious devices and crowdsourced detection, turning every user into a sensor.  
- **Impact:** This will bring safer communities, reduced fraud, and a flexible platform that can be adapted to other community risk problems (e.g., campus safety, environmental hazards).  
- **Future Vision:**  
  - BLE simulation for scanner testing (planned, not yet implemented).  
  - Ethical hardware integration.  
  - Expansion to other fraud vectors.  

## Next Steps
- Deploy to iOS and Android  
- Add authentication for verified reporters  
- Expand mobile-first UI/UX  
- Draft risk policy preamble highlighting engineers’ social responsibility  

## Built With
- **Python** – core language for backend and detection logic
- **Flask** – web framework for serving the interactive map
- **Folium** – map rendering and visualization
- **GeoJSON** – standardized format for location-based reporting
- **Firebase Firestore** – cloud database for storing reports
- **SQLite** – local caching and lightweight storage
- **Wi‑Fi scanning** – primary detection method for identifying suspicious signals
- **FastAPI** – framework powering the MCP server
- **Uvicorn** – ASGI server for running FastAPI
- **Pydantic** – data validation and modeling for Wi‑Fi scans
- **OpenAI API** – AI analysis of suspicious Wi‑Fi signals
- **dotenv** – environment variable management
- **Logging** – structured logging for server and AI calls
- **UUID** – unique identifiers for detections
- **MCP Server** – modular expansion layer for connecting external services\
- **Rasberry Pi** - used to simulate fake skimmer signal
- **Thony** - IDE for writing and flashing MicroPython code onto the Rasbery Pi
- **Micro Python** - runtime envrionment for embedded scripting
- **time** - used for delays and keeping BLE advertisements alive
- **network** - configured the Rasbery Pi to broadcast Wi-Fi
- **bluetooth** - enabled BLE advertising on Rasbery Pi
- **struct** – built proper BLE advertising packets for detection by scanners


## Resources
Documentation to read to understand what an MCP server is:

- [Official MCP Documentation](https://modelcontextprotocol.io/introduction)  
- [MCP Specification](https://spec.modelcontextprotocol.io/)  
- [Anthropic's MCP Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)  
- [MCP Quickstart](https://modelcontextprotocol.io/quickstart)  
- [Google Doc 1](https://docs.google.com/document/d/1ydh3ZT-ud5FvQoVlMNtsh3oE69U0uEI1_MA06HU3yJ0/edit?usp=sharing)  
- [Google Doc 2](https://docs.google.com/document/d/1OyiDoD6UcGc1kpnEXUeVxG4Y8LptLRVyxVNqYOajHEw/edit?usp=sharing)  


