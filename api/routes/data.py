import time
import uuid
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import UnifiedData
from schemas.api_response import APIResponse
from api.dependencies import verify_api_key

router = APIRouter()

@router.get("/data", response_model=APIResponse)
def get_data(
    request: Request,
    source: str = Query(None, description="Filter by data source (e.g., api, csv)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key) # Secure the endpoint
):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Build the query
    query = db.query(UnifiedData)
    
    # Apply Filtering
    if source:
        query = query.filter(UnifiedData.source == source)

    # Apply Pagination
    offset = (page - 1) * limit
    total_count = query.count()
    data = query.offset(offset).limit(limit).all()

    # Calculate Latency
    latency = (time.time() - start_time) * 1000

    return {
        "request_id": request_id,
        "api_latency_ms": round(latency, 2),
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_records": total_count
        }
    }