"""
Structured logging configuration for production deployment
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from .config import settings

class ProductionFormatter(logging.Formatter):
    """Custom formatter for production logs"""
    
    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()
        
        # Add environment info
        record.environment = settings.ENVIRONMENT
        
        # Create structured log format
        if settings.ENVIRONMENT == "production":
            # JSON-like format for production
            log_format = (
                f"[{record.timestamp}] "
                f"LEVEL={record.levelname} "
                f"MODULE={record.name} "
                f"ENV={record.environment} "
                f"MSG=\"{record.getMessage()}\""
            )
            
            # Add extra fields if present
            if hasattr(record, 'user_id'):
                log_format += f" USER_ID={record.user_id}"
            if hasattr(record, 'request_id'):
                log_format += f" REQUEST_ID={record.request_id}"
            if hasattr(record, 'ip_address'):
                log_format += f" IP={record.ip_address}"
                
            return log_format
        else:
            # Human-readable format for development
            return f"[{record.timestamp}] {record.levelname}: {record.getMessage()}"

def setup_logging():
    """Configure logging for the application"""
    
    # Determine log level based on environment
    if settings.ENVIRONMENT == "production":
        log_level = logging.INFO
    elif settings.ENVIRONMENT == "testing":
        log_level = logging.WARNING
    else:
        log_level = logging.DEBUG
    
    # Create formatter
    formatter = ProductionFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers in production
    if settings.ENVIRONMENT == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)

def log_security_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
):
    """Log security-related events with additional context"""
    extra = {
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        **kwargs
    }
    
    logger.warning(f"SECURITY_EVENT: {event_type} - {message}", extra=extra)

def log_business_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    user_id: Optional[str] = None,
    **kwargs
):
    """Log business-related events"""
    extra = {
        'event_type': event_type,
        'user_id': user_id,
        **kwargs
    }
    
    logger.info(f"BUSINESS_EVENT: {event_type} - {message}", extra=extra)

# Initialize logging when module is imported
setup_logging()