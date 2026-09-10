from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class EventCreate(BaseModel):
    event_type: str = Field(min_length=2, max_length=64)
    username: str | None = Field(default=None, max_length=128)
    source_ip: str | None = Field(default=None, max_length=45)
    message: str = Field(min_length=1, max_length=2000)

class EventResponse(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    severity: str
    risk_score: int
    created_at: datetime

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    severity: str
    risk_score: int
    source_ip: str | None
    technique: str | None
    status: str
    created_at: datetime
