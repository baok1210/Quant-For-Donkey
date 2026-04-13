"""
Retry utility with backoff for API calls
"""
import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry a function with exponential backoff
    
    Args:
        func: Function to call
        max_retries: Maximum number of retry attempts
        backoff_seconds: Initial backoff time in seconds
        backoff_factor: Multiplier for each retry
        exceptions: Tuple of exceptions to catch
    
    Returns:
        Result of func call
    """
    last_exception = None
    current_backoff = backoff_seconds
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} after error: {e}. "
                    f"Waiting {current_backoff}s..."
                )
                time.sleep(current_backoff)
                current_backoff *= backoff_factor
            else:
                logger.error(f"All {max_retries} retries exhausted. Last error: {e}")
    
    raise last_exception


def get_retry_config() -> dict:
    """Get retry config from settings or defaults"""
    try:
        import json
        import os
        config_path = os.path.join(os.path.dirname(__file__), "..", "config_settings.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
                return config.get("API_RETRY", {"max_retries": 3, "backoff_seconds": 2})
    except:
        pass
    return {"max_retries": 3, "backoff_seconds": 2}