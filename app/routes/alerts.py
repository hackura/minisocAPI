from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth import require_api_key
from app.db import get_db
from app.models import Alert
from app.schemas import AlertResponse

router = APIRouter(dependencies=[Depends(require_api_key)])

@router.get("", response_model=list[AlertResponse])
def list_alerts(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity.lower())
    if status:
        query = query.filter(Alert.status == status.lower())
    return query.order_by(Alert.created_at.desc()).limit(limit).all()
