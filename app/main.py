from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
from .config import settings
from .services.permit import PermitService
from .api import search_router, health_router, logs_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize permit service
permit_service = None


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(search_router)
    app.include_router(logs_router)
    
    return app

app = create_app()


@app.on_event("startup")
async def startup_event():
    global permit_service
    try:
        permit_service = PermitService(
            openai_api_key=settings.openai_api_key,
            pinecone_api_key=settings.pinecone_api_key,
            pinecone_environment=settings.pinecone_environment
        )
        logger.info("Permit service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize permit service: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    ) 