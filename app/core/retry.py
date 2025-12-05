# app/core/retry.py
"""
Reusable retry decorator for transient failures.
"""

import time
import functools
from typing import Callable, Type


def retry(
    attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    """
    Retry a function call if it raises one of the given exceptions.

    Args:
        attempts: Number of retry attempts.
        delay: Seconds to wait between attempts.
        exceptions: Tuple of exception types to retry.

    Usage:
        @retry(attempts=3, delay=2)
        def send_email(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator
