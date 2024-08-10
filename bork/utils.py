from inspect import get_annotations, getmembers, signature, isclass, isfunction
from functools import wraps
from typing import no_type_check
import logging

@no_type_check
def scoped_cache(cls):
    assert isclass(cls), f"scoped_cache is applied to classes, got a '{type(cls)}'"

    annotations = get_annotations(cls)
    sentinel = object()         # A unique value used as a sentinel for the cache
    dlog = logging.getLogger()  # The decorator's logger
    dlog.info(f"Making '{cls.__qualname__}' memoized")

    # object's methods are shown as functions on the class object
    zeroaries, dicts = set(), set()

    def zeroary_wrapper(f):
        dlog.debug(f"Memoizing zero-ary '{name}'")
        flog = logging.getLogger(f.__qualname__)  # the wrapper's logger

        attr_name = f"_{f.__name__}"
        assert attr_name not in zeroaries, "Somehow got multiple methods with the same name?"
        zeroaries.add(attr_name)

        @wraps(f)
        def g(self):
            res = object.__getattr__(self, attr_name)
            if res is not sentinel:
                return res

            flog.debug("Caching the first call")
            res = f(self)
            object.__setattr__(self, attr_name, res)  # so this works on frozen dataclasses etc.
            return res

        return g

    def unary_wrapper(f):
        # TODO: handle the case of a kw-only unary
        dlog.debug(f"Memoizing unary '{name}'")
        flog = logging.getLogger(f.__qualname__)  # the wrapper's logger

        attr_name = f"_{f.__name__}"
        assert attr_name not in dicts, "Somehow got multiple methods with the same name?"
        dicts.add(attr_name)

        @wraps(f)
        def g(self, x):
            cache = object.__getattr__(self, attr_name)
            if x in cache:
                return cache[x]

            flog.debug(f"Cache miss for '{x}'")
            res = f(self, x)
            cache[x] = res
            return res

        return g

    def nary_wrapper(f):
        dlog.debug(f"Memoizing n-ary '{name}'")
        flog = logging.getLogger(f.__qualname__)  # the wrapper's logger

        attr_name = f"_{f.__name__}"
        assert attr_name not in dicts, "Somehow got multiple methods with the same name?"
        dicts.add(attr_name)

        @wraps(f)
        def g(self, *args, **kwargs):
            cache = object.__getattr__(self, attr_name)
            key = (args, kwargs)
            if key in cache:
                return cache[key]

            flog.debug(f"Cache miss for '{key}'")
            res = f(self, *args, **kwargs)
            cache[key] = res
            return res

        return g


    for (name, f) in getmembers(cls, isfunction):
        if name.startswith("_") or getattr(f, '_do_not_cache', False):
            dlog.debug(f"Skipping '{name}'")
            continue

        assert name == f.__name__
        if f"_{name}" in annotations:
            raise ValueError(f"Memoization would use attribute '_{f.__name__}' which is already defined on the class")

        sig = signature(f)
        assert "self" in sig.parameters, f"Method '{f.__qualname__}' did not take 'self'"
        match len(sig.parameters):
            case 0:
                assert False
            case 1:
                setattr(cls, name, zeroary_wrapper(f))
            case 2:
                setattr(cls, name, unary_wrapper(f))
            case n if n > 2:
                setattr(cls, name, nary_wrapper(f))


    zeroaries, dicts = frozenset(zeroaries), frozenset(dicts)
    assert zeroaries.isdisjoint(dicts), "Somehow got multiple methods with the same name?"

    orig_init = cls.__init__
    @wraps(orig_init)
    def init(self, *args, **kwargs):
        for k in zeroaries:
            object.__setattr__(self, k, sentinel)
        for k in dicts:
            object.__setattr__(self, k, {})

        orig_init(self, *args, **kwargs)

    # TODO(nicoo) support __slots__
    cls.__init__ = init
    return cls


def _not_cached(f):
    f._do_not_cache = True
    return f

scoped_cache.skip = _not_cached
