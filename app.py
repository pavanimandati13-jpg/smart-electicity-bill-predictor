import os, sqlite3, datetime
from flask import Flask, jsonify, render_template, request, g
from billing import calculate_bill, load_tariff
import predictor

app = Flask(__name__)
DB = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "history.db"))

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, month INTEGER,
            units REAL, amount REAL)""")
    return g.db

@app.teardown_appcontext
def close(_):
    d = g.pop("db", None)
    if d: d.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/api/tariff")
def tariff():
    return jsonify(load_tariff())

@app.route("/api/predict", methods=["POST"])
def predict():
    d = request.get_json(force=True)
    try:
        args = [int(d["month"]), float(d["avg_temp"]), int(d["occupants"]),
                float(d["ac_hours"]), float(d["prev_units"]), float(d["prev2_units"])]
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Invalid or missing input fields"), 400
    if not 1 <= args[0] <= 12:
        return jsonify(error="month must be 1-12"), 400
    units, name, mae = predictor.predict_units(*args)
    bill = calculate_bill(units)
    c = db()
    c.execute("INSERT INTO predictions(created,month,units,amount) VALUES(?,?,?,?)",
              (datetime.datetime.utcnow().isoformat(), args[0], round(units, 2), bill["total"]))
    c.commit()
    return jsonify(predicted_units=round(units, 2), model=name, mae=round(mae, 2), bill=bill)

@app.route("/api/bill", methods=["POST"])
def bill():
    try:
        units = float(request.get_json(force=True)["units"])
    except (KeyError, ValueError, TypeError):
        return jsonify(error="units required"), 400
    return jsonify(calculate_bill(units))

@app.route("/api/history")
def history():
    rows = db().execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20").fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False)
