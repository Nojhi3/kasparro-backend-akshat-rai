from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

# This defines what your "Clean" data MUST look like.
# If data doesn't match this, Pydantic will throw an error (which is good!)
class UnifiedRow(BaseModel):
    entity_name: str
    value: float
    event_timestamp: datetime
    source: str
    original_id: str

    # Example Validator: Ensure value is positive
    @field_validator('value')
    @classmethod
    def value_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError('must be positive')
        return v