"""
Structured logging for the Quant system
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str = "quant_donkey",
    log_file: str = "logs/quant.log",
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup logger with file rotation and console output
    """
    # Create logs directory if not exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Default logger instance
default_logger = setup_logger()


def log_api_call(logger: logging.Logger, endpoint: str, status: str, details: str = ""):
    """Log API call with structured format"""
    logger.info(f"API | {endpoint} | {status} | {details}")


def log_analysis(logger: logging.Logger, module: str, result: str, details: str = ""):
    """Log analysis result"""
    logger.info(f"ANALYSIS | {module} | {result} | {details}")


def log_error(logger: logging.Logger, module: str, error: str, context: str = ""):
    """Log error with context"""
    logger.error(f"ERROR | {module} | {error} | Context: {context}")