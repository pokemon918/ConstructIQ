from fastapi import APIRouter, HTTPException, Depends
import logging

from ..models.common import HealthResponse, RootResponse
from ..services.permit import PermitService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


def get_permit_service() -> PermitService:
    from ..main import permit_service
    if not permit_service:
        raise HTTPException(status_code=503, detail="Permit service not available")
    return permit_service


@router.get("/", response_model=RootResponse)
async def root():
    return RootResponse(
        message="ConstructIQ Permit Search API",
        version="1.0.0",
        status="running"
    )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    permit_service: PermitService = Depends(get_permit_service)
):
    try:
        status = permit_service.get_service_status()
        return HealthResponse(
            status="OK",
            services=status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

