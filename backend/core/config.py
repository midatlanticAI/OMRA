"""
Configuration settings for the OpenManus application.
Loads environment variables and provides settings for various components.
"""
import os
from typing import Optional, Dict, Any, List

from pydantic import BaseSettings, PostgresDsn, validator, AnyHttpUrl, Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    PROJECT_NAME: str = "OMRA Appliance Repair Business Automation System"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ALGORITHM: str = "HS256"
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # For encrypting sensitive data
    
    # Database
    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL", "")
    SYNC_DATABASE_URL: Optional[str] = None
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "omra")
    
    # AI Services
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Third-party integrations
    GHL_API_KEY: Optional[str] = os.getenv("GHL_API_KEY", "")
    GHL_LOCATION_ID: Optional[str] = os.getenv("GHL_LOCATION_ID", "")
    KICKSERV_API_KEY: Optional[str] = os.getenv("KICKSERV_API_KEY", "")
    KICKSERV_ACCOUNT: Optional[str] = os.getenv("KICKSERV_ACCOUNT", "")
    
    # Application settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    AUDIT_LOG_ENABLED: bool = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    AUDIT_LOG_FILE: str = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")
    
    @validator("SYNC_DATABASE_URL", pre=True)
    def assemble_sync_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if values.get("DATABASE_URL"):
            # Convert async URL to sync URL for migrations
            return values.get("DATABASE_URL").replace("asyncpg", "psycopg2")
        return v
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Optional[str]) -> List[AnyHttpUrl]:
        if isinstance(v, str) and not v.startswith("["):
            return [item.strip() for item in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 