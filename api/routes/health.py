from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db
from core.models import ETLCheckpoint
from schemas.api_response import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    # 1. Check DB Connectivity
    db_status = False
    try:
        db.execute(text("SELECT 1"))
        db_status = True
    except Exception:
        db_status = False

    # 2. Check ETL Status (P0.2 requirement)
    # We fetch the most recent checkpoint
    last_run = db.query(ETLCheckpoint).order_by(ETLCheckpoint.updated_at.desc()).first()
    etl_status = last_run.last_run_status if last_run else "never_run"

    return {
        "status": "healthy" if db_status else "unhealthy",
        "db_connectivity": db_status,
        "etl_last_run_status": etl_status
    }