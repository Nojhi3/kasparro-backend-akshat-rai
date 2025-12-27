import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from core.database import Base

# -----------------------------
# Raw API Data
# -----------------------------
class RawAPIData(Base):
    __tablename__ = "raw_api_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name = Column(String, index=True)
    payload = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)


# -----------------------------
# Raw CSV Data
# -----------------------------
class RawCSVData(Base):
    __tablename__ = "raw_csv_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    row_data = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)


# -----------------------------
# Unified Data
# -----------------------------
class UnifiedData(Base):
    __tablename__ = "unified_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_name = Column(String, index=True)
    value = Column(Float)
    event_timestamp = Column(DateTime(timezone=True))
    source = Column(String)
    original_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# -----------------------------
# ETL Checkpoints
# -----------------------------
class ETLCheckpoint(Base):
    __tablename__ = "etl_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, index=True)
    last_processed_timestamp = Column(DateTime(timezone=True), nullable=True)
    last_processed_id = Column(String, nullable=True)
    last_run_status = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
