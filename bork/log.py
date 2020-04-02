import inspect
import logging
import sys
from typing import Any, Callable, cast, Dict, Optional, TypeVar


# Index mapping file names to module names.
_module_index: Dict[str, str] = {}


def _get_module(context: inspect.FrameInfo) -> str:
    """Find the module name for a given FrameInfo.

    Raises KeyError if the module isn't loaded.

    Pilfered from Jamie Bliss' equivalent in pursuedpybear:
      https://github.com/ppb/pursuedpybear/blob/master/ppb/utils.py
    """
    global _module_index  # pylint: disable=global-statement
    if context.filename not in _module_index:
        _module_index = {
            mod.__file__: mod.__name__
            for mod in sys.modules.values()
            if hasattr(mod, '__file__') and hasattr(mod, '__name__')
        }

    return _module_index[context.filename]


def logger(context: Optional[inspect.FrameInfo] = None) -> logging.Logger:
    """Provide a logger with a name appropriate for a given context.

    The default context is the caller's.
    """
    if context is None:
        context = inspect.getframeinfo(inspect.currentframe().f_back)  # type: ignore

    if context is None:
        # This may not be the best way to handle it, but if we get here
        # it'll avoid causing errors, at least.
        return logging.getLogger('??.??')

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

    # Cast required, as mypy cannot (yet?) type decorators usefully:
    #  https://github.com/python/mypy/issues/3157
    return cast(F, wrapper)
