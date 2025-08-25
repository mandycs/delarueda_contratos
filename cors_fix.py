#!/usr/bin/env python3
"""
Temporary CORS configuration fix for immediate deployment
"""

def get_cors_origins(environment="development"):
    """
    Get CORS origins based on environment
    Simple fallback configuration that works
    """
    if environment == "production":
        # In production, should be specific domains
        return [
            "https://delarueda-firmacontratosfront-cl4otx.dokploy.cc",
            "https://firmacontratos.delarueda.es",
            "https://www.delarueda.es"
        ]
    else:
        # Development - allow common local ports
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ]

def get_cors_config(environment="development"):
    """
    Get complete CORS middleware configuration
    """
    origins = get_cors_origins(environment)
    
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With"
        ],
    }

if __name__ == "__main__":
    import os
    env = os.getenv("ENVIRONMENT", "development")
    config = get_cors_config(env)
    print(f"CORS config for {env}:")
    for key, value in config.items():
        print(f"  {key}: {value}")