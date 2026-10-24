import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
import app as appmod
from billing import calculate_bill

def test_zero_units():
    assert calculate_bill(0)["energy_charge"] == 0

def test_slab_progression():
    assert calculate_bill(150)["energy_charge"] == 125.0
    assert calculate_bill(300)["energy_charge"] == 250 + 450

def test_api():
    c = appmod.app.test_client()
    r = c.post("/api/predict", json=dict(month=5, avg_temp=33, occupants=4, ac_hours=120, prev_units=280, prev2_units=260))
    assert r.status_code == 200 and r.get_json()["predicted_units"] > 0
    assert c.post("/api/predict", json={}).status_code == 400
    assert c.get("/health").get_json()["status"] == "ok"

if __name__ == "__main__":
    test_zero_units(); test_slab_progression(); test_api(); print("all tests passed")
