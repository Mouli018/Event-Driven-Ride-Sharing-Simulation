from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import time
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import secrets
import os

# Production Hardening: Disable docs in production/CI
app = FastAPI(
    title="Matching & Status Service",
    docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc"
)

# Security: Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Restrict this in production
)

# Security: CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: Secure Headers Layer
@app.middleware("http")
async def security_header_middleware(request, call_next):
    # Process request and get response
    res = await call_next(request)
    # Add essential security headers
    res.headers["X-Frame-Options"] = "DENY"
    res.headers["X-Content-Type-Options"] = "nosniff"
    res.headers["X-XSS-Protection"] = "1; mode=block"
    return res

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
        # Simulate driver matching delay (0.1s to 0.5s)
        time.sleep(0.1 + (secrets.randbelow(40) / 100))
        assigned_driver = secrets.choice(DRIVERS)
        MATCH_COUNTER.inc()

    matches_db[req.ride_id] = {
        "ride_id": req.ride_id,
        "driver": assigned_driver,
        "status": "driver_assigned",
        "eta_minutes": 2 + secrets.randbelow(9) # 2 to 10 minutes
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
    return {"status": "ok", "service": "matching-engine"}
