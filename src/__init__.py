from collections.abc import Callable
from functools import wraps

import bottle

from src import crud, utils


def cache(func: Callable) -> Callable:
    """Decorator used to cache HTTP responses."""

    @wraps(func)
    def wrapper(*args: str, **kwargs: str) -> str:
        # If Bottle is run in debug mode, then we do not use the cache
        if bottle.DEBUG:  # pragma: nocover
            return func(*args, **kwargs)

        # The cache key is computed from the request path, first
        params = bottle.request.params
        # Then optional data
        key = "-".join(params.get(param, "") for param in ("checkpoint", "order", "subscription"))
        key = utils.cache_key(f"{bottle.request.path}-{key}")

        return crud.read(key) or crud.create(key, func(*args, **kwargs))

    return wrapper

__all__ = ("cache",)
