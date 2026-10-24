"""Predict next-month consumption (kWh) from history + temperature + appliance load."""
import os, pickle
import numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "data", "consumption.csv")
MODEL = os.path.join(BASE, "model", "model.pkl")
FEATURES = ["month", "avg_temp", "occupants", "ac_hours", "prev_units", "prev2_units"]

def make_features(df):
    df = df.copy()
    if "household" not in df.columns:
        df["household"] = 0
    g = df.groupby("household")["units"]
    df["prev_units"] = g.shift(1)
    df["prev2_units"] = g.shift(2)
    return df.dropna()

def train():
    df = make_features(pd.read_csv(DATA))
    X, y = df[FEATURES], df["units"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    candidates = {"ridge": Ridge(alpha=1.0),
                  "gbr": GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=42)}
    best, best_mae, best_name = None, 1e9, ""
    for name, m in candidates.items():
        m.fit(Xtr, ytr)
        mae = mean_absolute_error(yte, m.predict(Xte))
        if mae < best_mae:
            best, best_mae, best_name = m, mae, name
    best.fit(X, y)
    os.makedirs(os.path.dirname(MODEL), exist_ok=True)
    with open(MODEL, "wb") as f:
        pickle.dump({"model": best, "name": best_name, "mae": best_mae}, f)
    return best_name, best_mae

def _load():
    if not os.path.exists(MODEL):
        train()
    with open(MODEL, "rb") as f:
        return pickle.load(f)

def predict_units(month, avg_temp, occupants, ac_hours, prev_units, prev2_units):
    bundle = _load()
    row = pd.DataFrame([[month, avg_temp, occupants, ac_hours, prev_units, prev2_units]], columns=FEATURES)
    return max(0.0, float(bundle["model"].predict(row)[0])), bundle["name"], bundle["mae"]

if __name__ == "__main__":
    print("Trained %s, MAE=%.2f kWh" % train())
