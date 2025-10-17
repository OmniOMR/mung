import time
import functools
from contextlib import contextmanager
import logging
from typing import Optional


@contextmanager
def log_time(msg: str, logger: logging.Logger, level: Optional[int] = None):
    """
    Context manager to measure and log elapsed time.
    """
    level = logging.INFO if level is None else level
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.log(level, f"{msg}. In {elapsed:.3f} seconds.")


def timeit(msg: str, logger: logging.Logger, level: Optional[int] = None):
    """
    Decorator to measure and log elapsed time of a function.
    """
    level = logging.INFO if level is None else level

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                logger.log(level, "%s finished in %.3f seconds", func.__qualname__, elapsed)

        return wrapper
    return decorator
