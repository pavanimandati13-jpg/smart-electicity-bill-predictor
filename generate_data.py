"""Generates a synthetic household consumption dataset (replace with real meter data)."""
import numpy as np, pandas as pd, os
rng = np.random.default_rng(7)
rows = []
for h in range(40):                      # 40 households x 36 months
    occ = int(rng.integers(1, 7)); base = 60 + occ * 28 + rng.normal(0, 15)
    ac_owner = rng.random() < 0.7
    for i in range(36):
        month = i % 12 + 1
        temp = 27 + 7 * np.sin((month - 3) / 12 * 2 * np.pi) + rng.normal(0, 1.2)
        ac = max(0, (temp - 26) * 45 * rng.uniform(0.6, 1.2)) if ac_owner else 0
        units = base + ac * 1.35 + (temp - 27) * 3 + rng.normal(0, 12)
        rows.append([h, month, round(temp, 1), occ, round(ac, 1), round(max(units, 20), 1)])
df = pd.DataFrame(rows, columns=["household", "month", "avg_temp", "occupants", "ac_hours", "units"])
# keep shift() inside each household valid: handled in predictor via per-household ordering
os.makedirs("data", exist_ok=True)
df.to_csv("data/consumption.csv", index=False)
print("rows:", len(df))
