# detection/ble_detect.py
import os
import joblib
import numpy as np

MODEL_PATH = "trained_models/ble_model.pkl"
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

def detect_ble_anomaly(rssi, adv_count=0, connectable=0):
    if model is None:
        return None
    # IsolationForest expects an array of features; adjust if your model expects other features
    X = np.array([[rssi if rssi is not None else 0, adv_count, connectable]])
    pred = model.predict(X)[0]
    return pred == -1
