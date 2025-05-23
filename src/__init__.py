"""Simple file cache for the Python Bottle web framework. 

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-simple-cache
"""
from collections.abc import Callable
from contextlib import suppress
from functools import wraps
from hashlib import md5
from pathlib import Path
from time import monotonic
from zlib import compress, decompress

import bottle


#
# Constants
#

ADD_HEADER = True
DELAY_BEFORE_EXPIRATION_IN_SEC = 10 * 60
FILES_CACHE = Path(__file__).parent.parent / "cache"
HEADER_NAME = "Cached-Since"
ONE_MINUTE_IN_SEC = 60

#
# Utilities
#

def cache_key(key: str) -> str:
    return md5(key.encode(), usedforsecurity=False).hexdigest()


#
# CRUD
#

def create(key: str, value: str) -> str:
    """Store a HTTP response into a compressed cache file."""
    file = FILES_CACHE / f"{key}.cache"
    data = f"{int(monotonic())}|{value}".encode()
    file.write_bytes(compress(data, level=9))
    return value


def read(key: str) -> str | None:
    """Retreive a response from a potential cache file."""
    file = FILES_CACHE / f"{key}.cache"

    with suppress(FileNotFoundError):
        when, page = decompress(file.read_bytes()).decode().split("|", 1)
        if (diff := int(monotonic()) - int(when)) < DELAY_BEFORE_EXPIRATION_IN_SEC:
            if ADD_HEADER:
                bottle.response.headers.append(HEADER_NAME, f"{diff / ONE_MINUTE_IN_SEC:0.2f} min")
            return page

        delete(key)

    return None


def delete(key: str) -> None:
    (FILES_CACHE / cache_key(key)).unlink(missing_ok=True)


#
# The decorator
#

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
        key = cache_key(f"{bottle.request.path}-{key}")

        return read(key) or create(key, func(*args, **kwargs))

    return wrapper

__all__ = ("cache",)
