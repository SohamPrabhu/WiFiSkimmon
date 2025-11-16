# tools.py
WIFI_TOOL = {
    "type": "function",
    "function": {
        "name": "wifi_risk_assessment",
        "description": "Assess WiFi devices for skimming risk.",
        "parameters": {
            "type": "object",
            "properties": {
                "assessments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "device_id": {"type": "string"},
                            "risk_score": {"type": "number"},
                            "confidence": {"type": "number"},
                            "explanation": {"type": "string"},
                            "recommendation": {"type": "string"},
                        },
                        "required": [
                            "device_id",
                            "risk_score",
                            "confidence",
                            "explanation",
                            "recommendation",
                        ],
                    },
                }
            },
            "required": ["assessments"],
        },
    },
}
