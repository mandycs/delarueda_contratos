from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
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
