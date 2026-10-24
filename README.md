# Cloud Based Smart Electricity Bill Predictor

Predicts a household's next-month electricity consumption (kWh) using machine learning
and converts it to a bill using slab-based tariff rules. Packaged as a Flask web app that
deploys to any cloud (Docker / Render / Heroku / Google App Engine / AWS / Azure).

## Features
- ML model (Ridge vs Gradient Boosting, best chosen by MAE) on temperature, occupants, AC hours, last 2 months' usage
- Slab-wise bill breakdown with fixed charge and tax (editable in `tariff.json`)
- REST API + web dashboard, prediction history stored in SQLite
- Health endpoint for cloud monitoring, Dockerfile, Procfile, app.yaml

## Architecture
Browser UI -> Flask REST API (`app.py`) -> `predictor.py` (scikit-learn) + `billing.py` (tariff engine) -> SQLite history

## Run locally
```bash
pip install -r requirements.txt
python generate_data.py      # synthetic dataset (replace data/consumption.csv with real data)
python predictor.py          # trains model -> model/model.pkl
python app.py                # http://localhost:8080
pytest tests                 # optional (pip install pytest)
```

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/predict` | body: month, avg_temp, occupants, ac_hours, prev_units, prev2_units |
| POST | `/api/bill` | body: units -> bill breakdown |
| GET | `/api/history` | last 20 predictions |
| GET | `/api/tariff` | current tariff |
| GET | `/health` | liveness check |

## Deploy to cloud
**Docker (any provider):**
```bash
docker build -t bill-predictor . && docker run -p 8080:8080 bill-predictor
```
**Render / Heroku:** push repo; build `pip install -r requirements.txt && python generate_data.py && python predictor.py`; start command from `Procfile`.
**Google App Engine:** train model first, then `gcloud app deploy`.
**AWS Elastic Beanstalk / Azure App Service:** deploy the folder as a Python web app, start command `gunicorn app:app`.

## Notes
- The dataset is synthetic for demo; use real meter readings for accurate results.
- Tariff slabs are sample values - update `tariff.json` to your board's current rates.
- On ephemeral cloud disks SQLite history resets on redeploy; use a managed DB (RDS / Cloud SQL) for production.
