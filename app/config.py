from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):    
    # API Configuration
    api_title: str = "ConstructIQ Permit Search API"
    api_description: str = "Semantic search API for Austin building permits using vector embeddings"
    api_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS Configuration
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "austin-permits"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings() 