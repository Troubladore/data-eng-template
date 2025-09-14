from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class BronzeEvent(SQLModel, table=True):
    __tablename__ = "bronze_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)
    payload: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
