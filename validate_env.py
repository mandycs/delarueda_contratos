#!/usr/bin/env python3
"""
Environment validation script for production deployment
"""

import os
import sys
import secrets
from urllib.parse import urlparse
from typing import List, Tuple

def validate_environment() -> Tuple[bool, List[str]]:
    """Validate environment configuration for production deployment"""
    issues = []
    
    # Check required environment variables
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'SMTP_PASSWORD',
        'FRONTEND_URL'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"❌ Missing required environment variable: {var}")
    
    # Validate SECRET_KEY strength
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        if len(secret_key) < 32:
            issues.append("❌ SECRET_KEY must be at least 32 characters long")
        if secret_key in ['tu_clave_secreta_muy_larga_y_aleatoria_aqui', 'your-secret-key-change-in-production']:
            issues.append("❌ SECRET_KEY is using default/example value - SECURITY RISK!")
    
    # Validate DATABASE_URL format
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        try:
            parsed = urlparse(db_url)
            if not parsed.scheme.startswith('postgresql'):
                issues.append("❌ DATABASE_URL must use postgresql scheme")
            if not parsed.hostname:
                issues.append("❌ DATABASE_URL missing hostname")
            if not parsed.username:
                issues.append("❌ DATABASE_URL missing username")
            if not parsed.password:
                issues.append("❌ DATABASE_URL missing password")
        except Exception as e:
            issues.append(f"❌ Invalid DATABASE_URL format: {e}")
    
    # Validate ENVIRONMENT setting
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment == 'production':
        # Additional production checks
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
        if allowed_origins == '*':
            issues.append("⚠️  ALLOWED_ORIGINS is set to '*' in production - should restrict to specific domains")
    
    # Validate FRONTEND_URL
    frontend_url = os.getenv('FRONTEND_URL')
    if frontend_url:
        try:
            parsed = urlparse(frontend_url)
            if not parsed.scheme in ['http', 'https']:
                issues.append("❌ FRONTEND_URL must use http or https scheme")
            if environment == 'production' and parsed.scheme == 'http':
                issues.append("⚠️  FRONTEND_URL uses HTTP in production - consider HTTPS for security")
        except Exception as e:
            issues.append(f"❌ Invalid FRONTEND_URL format: {e}")
    
    # Check for development/testing passwords in production
    smtp_password = os.getenv('SMTP_PASSWORD')
    if smtp_password and smtp_password in ['tu_password_smtp_aqui', 'test', 'password']:
        issues.append("❌ SMTP_PASSWORD appears to be a default/test value - SECURITY RISK!")
    
    return len(issues) == 0, issues

def generate_secure_secret():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def main():
    print("🔍 Validating environment configuration...\n")
    
    is_valid, issues = validate_environment()
    
    if is_valid:
        print("✅ Environment configuration is valid for production!")
    else:
        print("❌ Environment configuration has issues:\n")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n💡 Suggestions:")
        print("  1. Update .env file with secure values")
        print("  2. Use the following command to generate a secure SECRET_KEY:")
        print(f"     python3 -c \"import secrets; print('SECRET_KEY={secrets.token_urlsafe(32)}')\"")
        print("  3. Ensure all passwords are changed from default values")
        print("  4. In production, set ALLOWED_ORIGINS to specific domains")
        
        sys.exit(1)

if __name__ == "__main__":
    main()