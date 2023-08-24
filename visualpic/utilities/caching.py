# The `lru_cache` decorator has the problem that it breaks type checking as
# well as code suggestions in IDEs. The code below is a workaround (see
# https://github.com/python/mypy/issues/5107) that only actually imports
# `lru_cache` at run time.
from typing import TYPE_CHECKING, TypeVar, Callable
if TYPE_CHECKING:
    F = TypeVar('F', Callable)
    def lru_cache(f: F) -> F: pass
else:
    from functools import lru_cache


__all__ = ['lru_cache']
