from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import logging
import uuid
import os
import json
import tools
import prompts

# ============================================================
# Init
# ============================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Models
# ============================================================
class WifiScanInput(BaseModel):
    timestamp: datetime
    mac: str
    name: Optional[str] = None
    bssid: str
    ssid: Optional[str] = None
    rssi: int
    protocol: str
    model_score: Optional[float] = None

class RiskAssessmentResponse(BaseModel):
    detection_id: str
    mac: str
    bssid: str
    risk_score: int
    risk_level: str
    ai_comments: str

class StoredDetection(BaseModel):
    id: str
    mac: str
    bssid: str
    ssid: Optional[str] = None
    rssi: int
    protocol: str
    model_score: Optional[float] = None
    risk_score: int
    risk_level: str
    timestamp: datetime
    extra: Optional[dict] = None

# ============================================================
# Local Storage
# ============================================================
all_detections: List[dict] = []

# ============================================================
# Helpers
# ============================================================
def get_risk_level(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"

async def _call_model_with_tools(system_prompt: str, user_message: str, tool_def: dict) -> dict:
    """Call OpenAI with robust error handling and logging."""
    try:
        logger.info("Calling OpenAI for WiFi analysis...")
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            tools=[tool_def],
            tool_choice="required",
        )

        message = response.choices[0].message
        if not message.tool_calls:
            raise ValueError("No tool calls returned from OpenAI")

        call = message.tool_calls[0]
        args_str = call.function.arguments
        logger.info(f"OpenAI tool response: {args_str}")
        return json.loads(args_str)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from OpenAI: {e}\nRaw: {args_str}")
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")
    except Exception as e:
        logger.exception("OpenAI call failed")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

# ============================================================
# Analyze WiFi Scans
# ============================================================
async def analyze_scans(scans: List[WifiScanInput]) -> List[dict]:
    data = [s.model_dump() for s in scans]
    # In analyze_scans function, replace user_msg with:
    user_msg = f"""
    BEGIN WIFI SKIMMER ANALYSIS

    TOTAL SCANS: {len(data)}
    DEVICES TO ANALYZE (by bssid):
    {', '.join([f'"{s.get("bssid") or s.get("mac")}"' for s in data])}

    FULL DATA:
    {json.dumps(data, indent=2, default=str)}

    INSTRUCTIONS:
    - Return EXACTLY one assessment per device
    - Use `device_id` = bssid (or mac)
    - DO NOT SKIP ANY DEVICE
    - Include risk_score, confidence, explanation, recommendation
    """


    result = await _call_model_with_tools(prompts.WIFI_SYSTEM_PROMPT, user_msg, tools.WIFI_TOOL)
    return result.get("assessments", [])

# ============================================================
# Routes
# ============================================================
@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.post("/api/detectwifi", response_model=List[RiskAssessmentResponse])
async def detect_wifi(scans: List[WifiScanInput]):
    if not scans:
        raise HTTPException(status_code=400, detail="No scan data provided")

    assessments = await analyze_scans(scans)
    if not assessments:
        logger.warning("OpenAI returned no assessments")
        raise HTTPException(status_code=500, detail="No risk assessments returned")

    responses = []

    for assess in assessments:
        device_id = assess.get("device_id")
        if not device_id:
            logger.warning(f"Assessment missing device_id: {assess}")
            continue

        # Find matching scan by bssid or mac
        matched_scan = None
        for scan in scans:
            if scan.bssid == device_id or scan.mac == device_id:
                matched_scan = scan
                break

        if not matched_scan:
            logger.warning(f"No scan found for device_id: {device_id}")
            continue

        detection_id = str(uuid.uuid4())
        score = max(0, min(100, int(assess.get("risk_score", 0))))
        level = get_risk_level(score)
        confidence_pct = int(float(assess.get("confidence", 0)) * 100)

        comments = (
            f"{assess.get('explanation', 'No explanation')} | "
            f"Recommendation: {assess.get('recommendation', 'N/A')} | "
            f"Confidence: {confidence_pct}%"
        )

        # Store detection
        stored = StoredDetection(
            id=detection_id,
            mac=matched_scan.mac,
            bssid=matched_scan.bssid,
            ssid=matched_scan.ssid,
            rssi=matched_scan.rssi,
            protocol=matched_scan.protocol,
            model_score=matched_scan.model_score,
            risk_score=score,
            risk_level=level,
            timestamp=matched_scan.timestamp,
            extra={"name": matched_scan.name}
        )
        all_detections.append(stored.model_dump())

        responses.append(RiskAssessmentResponse(
            detection_id=detection_id,
            mac=matched_scan.mac,
            bssid=matched_scan.bssid,
            risk_score=score,
            risk_level=level,
            ai_comments=comments,
        ))

    if not responses:
        raise HTTPException(status_code=500, detail="No valid assessments matched")

    return responses

@app.get("/api/detections", response_model=List[StoredDetection])
async def get_all():
    return all_detections

@app.get("/api/risk-analysis/{detection_id}")
async def get_analysis(detection_id: str):
    d = next((x for x in all_detections if x["id"] == detection_id), None)
    if not d:
        raise HTTPException(status_code=404, detail="Detection not found")
    return {"detection_id": detection_id, "stored": d}
