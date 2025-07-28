from .search import router as search_router
from .health import router as health_router
from .logs import router as logs_router

__all__ = ["search_router", "health_router", "logs_router"] 