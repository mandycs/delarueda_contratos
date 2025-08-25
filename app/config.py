from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS configuration
    ALLOWED_ORIGINS: Union[str, List[str]] = "*"  # Override in production with specific domains
    ENVIRONMENT: str = "development"  # production, development, testing
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def validate_allowed_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            # Split by comma and clean up whitespace
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            return origins if origins else ["*"]
        return ["*"]
    
    # Email configuration
    SMTP_SERVER: str = "email.sphyrnasolutions.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = "system@delarueda.es"
    SMTP_PASSWORD: str  # Will be set from environment
    SMTP_USE_TLS: bool = False  # Use SSL instead
    SMTP_USE_SSL: bool = True
    SMTP_FROM_EMAIL: str = "system@delarueda.es"
    SMTP_FROM_NAME: str = "Sistema de Contratos - De La Rueda"
    
    # Admin settings
    ADMIN_EMAIL: str  # Will be set from environment
    
    # Frontend URL for links
    FRONTEND_URL: str  # Will be set from environment

    class Config:
        env_file = ".env"

settings = Settings()
