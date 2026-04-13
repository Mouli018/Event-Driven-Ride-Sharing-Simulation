from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import random
import time
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Matching & Status Service")

MATCH_COUNTER = Counter("driver_matches_total", "Total driver matches made")
MATCH_LATENCY = Histogram("match_latency_seconds", "Time taken to match a driver")

DRIVERS = ["driver_A", "driver_B", "driver_C", "driver_D", "driver_E"]
matches_db = {}

class MatchRequest(BaseModel):
    ride_id: str
    pickup_location: str

@app.post("/match")
def match_driver(req: MatchRequest):
    with MATCH_LATENCY.time():
        # Simulate driver matching delay
        time.sleep(random.uniform(0.1, 0.5))
        assigned_driver = random.choice(DRIVERS)
        MATCH_COUNTER.inc()

    matches_db[req.ride_id] = {
        "ride_id": req.ride_id,
        "driver": assigned_driver,
        "status": "driver_assigned",
        "eta_minutes": random.randint(2, 10)
    }
    return matches_db[req.ride_id]

@app.get("/status/{ride_id}")
def get_status(ride_id: str):
    if ride_id not in matches_db:
        return {"ride_id": ride_id, "status": "pending"}
    return matches_db[ride_id]

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest())

@app.get("/health")
def healthz():
    return {"status": "ok"}
