from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS configuration
    ALLOWED_ORIGINS: str = "*"  # Override in production with specific domains
    ENVIRONMENT: str = "development"  # production, development, testing
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def validate_allowed_origins(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Email configuration
    SMTP_SERVER: str = "email.sphyrnasolutions.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = "system@delarueda.es"
    SMTP_PASSWORD: str  # Will be set from environment
    SMTP_USE_TLS: bool = False  # Use SSL instead
    SMTP_USE_SSL: bool = True
    SMTP_FROM_EMAIL: str = "system@delarueda.es"
    SMTP_FROM_NAME: str = "Sistema de Contratos - De La Rueda"
    
    # Frontend URL for links
    FRONTEND_URL: str  # Will be set from environment

    class Config:
        env_file = ".env"

settings = Settings()
