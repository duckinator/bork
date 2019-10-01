import inspect
import logging
import sys
from typing import Any, Callable, Optional, TypeVar


def _get_module(context: inspect.FrameInfo) -> str:
    """Find the module name for a given FrameInfo.

    Raises KeyError if the module isn't loaded.

    Pilfered from Jamie Bliss' equivalent in pursuedpybear:
      https://github.com/ppb/pursuedpybear/blob/master/ppb/utils.py
    """
    if context.filename not in _get_module.index:
        _get_module.index = {
            mod.__file__: mod.__name__
            for mod in sys.modules.values()
            if hasattr(mod, '__file__') and hasattr(mod, '__name__')
        }

    return _get_module.index[context.filename]


_get_module.index = {}


def logger(context: Optional[inspect.FrameInfo] = None) -> logging.Logger:
    """Provide a logger with a name appropriate for a given context.

    The default context is the caller's.
    """
    if context is None:
        context = inspect.getframeinfo(inspect.currentframe().f_back)

    return logging.getLogger('{}.{}'.format(_get_module(context), context.function))


F = TypeVar('F', bound=Callable[..., Any])


def trace(func: F, level: int = logging.DEBUG) -> F:
    """Decorator to log function entry and exit."""
    log = logging.getLogger('{}.{}'.format(func.__module__, func.__qualname__))

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
