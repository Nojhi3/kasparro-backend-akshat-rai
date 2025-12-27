from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# The shape of a single data item in the response
class DataItem(BaseModel):
    id: UUID
    entity_name: str
    value: float
    event_timestamp: datetime
    source: str

    class Config:
        from_attributes = True # Allows Pydantic to read from SQLAlchemy models

# The Metadata wrapper (P0.2 requirement)
class APIResponse(BaseModel):
    request_id: str
    api_latency_ms: float
    data: List[DataItem]
    pagination: dict

# Health Check Response
class HealthResponse(BaseModel):
    status: str
    db_connectivity: bool
    etl_last_run_status: Optional[str]

# Stats Response (P1.3 requirement)
class StatsResponse(BaseModel):
    total_records: int
    last_run_status: Optional[str]
    last_run_timestamp: Optional[datetime]