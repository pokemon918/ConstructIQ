from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import logging

from ..services.logging_service import QueryLoggingService
from ..api_config.api_version import LOGS_ROUTER_PREFIX

logger = logging.getLogger(__name__)

router = APIRouter(prefix=LOGS_ROUTER_PREFIX, tags=["logs"])

def get_logging_service() -> QueryLoggingService:
    return QueryLoggingService()

@router.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_logs(
    limit: int = 25,
    logging_service: QueryLoggingService = Depends(get_logging_service)
):
    if limit > 100:
        limit = 100
    
    try:
        logs = logging_service.get_recent_logs(limit=limit)
        return logs
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")
