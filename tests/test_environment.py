import pytest
import os
import tempfile
from validate_env import validate_environment

def test_validate_environment_missing_vars():
    """Test validation with missing required variables"""
    # Clear all environment variables
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'SMTP_PASSWORD', 'FRONTEND_URL']
    original_values = {}
    
    for var in required_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    try:
        is_valid, issues = validate_environment()
        assert not is_valid
        assert len(issues) >= 4  # At least 4 missing variables
        
        # Check that missing variables are reported
        issues_text = " ".join(issues)
        for var in required_vars:
            assert var in issues_text
    
    finally:
        # Restore original values
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value

def test_validate_environment_weak_secret():
    """Test validation with weak secret key"""
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'
    os.environ['SECRET_KEY'] = 'short'  # Too short
    os.environ['SMTP_PASSWORD'] = 'secure_password'
    os.environ['FRONTEND_URL'] = 'https://example.com'
    
    is_valid, issues = validate_environment()
    assert not is_valid
    
    issues_text = " ".join(issues)
    assert "SECRET_KEY must be at least 32 characters" in issues_text

def test_validate_environment_default_values():
    """Test validation with default/example values"""
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'
    os.environ['SECRET_KEY'] = 'tu_clave_secreta_muy_larga_y_aleatoria_aqui'  # Default value
    os.environ['SMTP_PASSWORD'] = 'secure_password'
    os.environ['FRONTEND_URL'] = 'https://example.com'
    
    is_valid, issues = validate_environment()
    assert not is_valid
    
    issues_text = " ".join(issues)
    assert "using default/example value" in issues_text

def test_validate_environment_invalid_database_url():
    """Test validation with invalid database URL"""
    os.environ['DATABASE_URL'] = 'invalid_url'
    os.environ['SECRET_KEY'] = 'a_very_long_and_secure_secret_key_that_is_definitely_over_32_characters'
    os.environ['SMTP_PASSWORD'] = 'secure_password'
    os.environ['FRONTEND_URL'] = 'https://example.com'
    
    is_valid, issues = validate_environment()
    assert not is_valid
    
    issues_text = " ".join(issues)
    assert "DATABASE_URL" in issues_text

def test_validate_environment_production_cors():
    """Test validation in production environment with wildcard CORS"""
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'
    os.environ['SECRET_KEY'] = 'a_very_long_and_secure_secret_key_that_is_definitely_over_32_characters'
    os.environ['SMTP_PASSWORD'] = 'secure_password'
    os.environ['FRONTEND_URL'] = 'https://example.com'
    os.environ['ALLOWED_ORIGINS'] = '*'
    
    is_valid, issues = validate_environment()
    assert not is_valid
    
    issues_text = " ".join(issues)
    assert "ALLOWED_ORIGINS is set to '*' in production" in issues_text

def test_validate_environment_valid_config():
    """Test validation with completely valid configuration"""
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://user:securepass@localhost/production_db'
    os.environ['SECRET_KEY'] = 'a_very_long_and_secure_secret_key_that_is_definitely_over_32_characters'
    os.environ['SMTP_PASSWORD'] = 'secure_smtp_password'
    os.environ['FRONTEND_URL'] = 'https://secure-domain.com'
    os.environ['ALLOWED_ORIGINS'] = 'https://secure-domain.com,https://www.secure-domain.com'
    
    is_valid, issues = validate_environment()
    assert is_valid
    assert len(issues) == 0