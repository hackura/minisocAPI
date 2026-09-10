from fastapi import FastAPI
from app.db import init_db
from app.routes import alerts, events, health

app = FastAPI(
    title="MiniSOC API",
    description="A lightweight defensive Security Operations Center API for security event ingestion, detection, risk scoring, and alerting.",
    version="1.0.0",
)

app.include_router(health.router, tags=["Health"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

@app.on_event("startup")
def startup() -> None:
    init_db()
