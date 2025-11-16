# detection/wifi_detect.py
import os
import joblib
import numpy as np

MODEL_PATH = "trained_models/wifi_model.pkl"
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

def detect_wifi_anomaly(rssi):
    if model is None:
        return None
    X = np.array([[rssi if rssi is not None else 0]])
    pred = model.predict(X)[0]
    return pred == -1
