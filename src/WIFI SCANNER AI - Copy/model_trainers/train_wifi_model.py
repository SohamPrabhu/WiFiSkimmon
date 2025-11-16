import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# --- CONFIG ---
DATA_PATH = "data/wifi_training_data.csv"  # path to your WiFi CSV
MODEL_PATH = "data/wifi_model.pkl"         # output model file

# --- LOAD CSV DATA ---
# Expected columns: rssi
print("📥 Loading WiFi training data...")
wifi_data = pd.read_csv(DATA_PATH)

# Verify data columns
if "rssi" not in wifi_data.columns:
    raise ValueError(f"❌ Missing 'rssi' column in CSV. Found: {wifi_data.columns}")

# --- TRAIN MODEL ---
print("🤖 Training WiFi Isolation Forest model...")
wifi_model = IsolationForest(
    contamination=0.05,  # tune this to make detection more or less sensitive
    random_state=42
)
wifi_model.fit(wifi_data[["rssi"]])

# --- SAVE MODEL ---
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(wifi_model, MODEL_PATH)
print(f"✅ WiFi model saved at: {MODEL_PATH}")
