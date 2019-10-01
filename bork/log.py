import inspect
import logging
from typing import Any, Callable, Optional, TypeVar


def logger(context: Optional[inspect.FrameInfo] = None) -> logging.Logger:
    """Provide a logger with a name appropriate for a given context.

    The default context is the caller's.
    """
    if context is None:
        context = inspect.getframeinfo(inspect.currentframe().f_back)

    return logging.getLogger('bork.{}'.format(context.function))


F = TypeVar('F', bound=Callable[..., Any])  # noqa


def trace(func: F, level: int = logging.DEBUG) -> F:
    """Decorator to log function entry and exit."""
    log = logging.getLogger(__name__ + func.__name__)

    def wrapper(*args, **kwargs):
        arglist = map(repr, args) + [
            '{}={}'.format(repr(k), repr(v)) for k, v in kwargs
        ]

        try:
            log.log(level, 'called with %s', ', '.join(arglist))
            return func(*args, **kwargs)
        finally:
            log.log(level, 'exiting')

    return wrapper
