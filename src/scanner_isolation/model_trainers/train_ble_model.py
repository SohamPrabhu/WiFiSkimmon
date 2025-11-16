import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# --- CONFIG ---
DATA_PATH = "data/ble_training_data.csv"   # path to your BLE CSV
MODEL_PATH = "data/ble_model.pkl"          # output model file

# --- LOAD CSV DATA ---
# Expected columns: rssi, adv_count, connectable
print("📥 Loading BLE training data...")
ble_data = pd.read_csv(DATA_PATH)

# Verify data columns
required_cols = {"rssi", "adv_count", "connectable"}
if not required_cols.issubset(ble_data.columns):
    raise ValueError(f"❌ Missing required columns in CSV. Found: {ble_data.columns}")

# --- TRAIN MODEL ---
print("🤖 Training BLE Isolation Forest model...")
ble_model = IsolationForest(
    contamination=0.05,  # % of expected anomalies
    random_state=42
)
ble_model.fit(ble_data[["rssi", "adv_count", "connectable"]])

# --- SAVE MODEL ---
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(ble_model, MODEL_PATH)
print(f"✅ BLE model saved at: {MODEL_PATH}")
