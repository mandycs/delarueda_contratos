import pytest
import os
from app.config import Settings

def test_cors_config_single_origin():
    """Test CORS configuration with single origin"""
    os.environ['ALLOWED_ORIGINS'] = 'https://example.com'
    settings = Settings()
    assert settings.ALLOWED_ORIGINS == ['https://example.com']

def test_cors_config_multiple_origins():
    """Test CORS configuration with multiple origins"""
    os.environ['ALLOWED_ORIGINS'] = 'https://example.com,https://www.example.com,https://app.example.com'
    settings = Settings()
    assert settings.ALLOWED_ORIGINS == ['https://example.com', 'https://www.example.com', 'https://app.example.com']

def test_cors_config_wildcard():
    """Test CORS configuration with wildcard"""
    os.environ['ALLOWED_ORIGINS'] = '*'
    settings = Settings()
    assert settings.ALLOWED_ORIGINS == ['*']

def test_cors_config_with_spaces():
    """Test CORS configuration with spaces around commas"""
    os.environ['ALLOWED_ORIGINS'] = 'https://example.com, https://www.example.com , https://app.example.com'
    settings = Settings()
    assert settings.ALLOWED_ORIGINS == ['https://example.com', 'https://www.example.com', 'https://app.example.com']

def test_environment_defaults():
    """Test default environment configuration"""
    # Clear environment specific vars
    for key in ['ENVIRONMENT', 'ALLOWED_ORIGINS']:
        if key in os.environ:
            del os.environ[key]
    
    settings = Settings(_env_file=None)
    assert settings.ENVIRONMENT == "development"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30