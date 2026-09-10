from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth import require_api_key
from app.db import get_db
from app.detection import analyze_event
from app.models import Alert, SecurityEvent
from app.schemas import EventCreate, EventResponse

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("", response_model=EventResponse, status_code=201)
def ingest_event(payload: EventCreate, db: Session = Depends(get_db)):
    score, severity, technique = analyze_event(payload.event_type, payload.source_ip)
    event = SecurityEvent(**payload.model_dump(), risk_score=score, severity=severity)
    db.add(event)
    db.flush()

    if technique:
        db.add(Alert(
            title="Possible brute-force authentication attack",
            severity=severity,
            risk_score=score,
            source_ip=payload.source_ip,
            technique=technique,
        ))
    db.commit()
    db.refresh(event)
    return event

@router.get("", response_model=list[EventResponse])
def list_events(
    severity: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(SecurityEvent)
    if severity:
        query = query.filter(SecurityEvent.severity == severity.lower())
    return query.order_by(SecurityEvent.created_at.desc()).limit(limit).all()
