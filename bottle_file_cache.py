"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

from contextlib import suppress
from functools import wraps
from hashlib import md5
from pathlib import Path
from time import time
from typing import TYPE_CHECKING
from zlib import compress, decompress

import bottle

if TYPE_CHECKING:
    from collections.abc import Callable

__version__ = "1.0.0"
__author__ = "Mickaël Schoentgen"
__copyright__ = f"""
Copyright (c) 2025, {__author__}
Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee or royalty is hereby
granted, provided that the above copyright notice appear in all copies
and that both that copyright notice and this permission notice appear
in supporting documentation or portions thereof, including
modifications, that you make.
"""

#
# Constants
#

# Files
DIR = Path(__file__).parent.parent / "cache"
FILE_EXT = "cache"

# Times
DELAY_BEFORE_EXPIRATION_IN_SEC = 10 * 60
ONE_MINUTE_IN_SEC = 60

# Special HTTP header injected to cached responses
APPEND_HEADER = True
HEADER_NAME = "Cached-Since"

# HTTP methods allowed to use the cache
HTTP_METHODS = ["GET"]


#
# Utilities
#


def cache_file(key: str) -> Path:
    """Get the cache file from the given `key`."""
    return DIR / f"{key}.{FILE_EXT}"


def cache_key(text: str) -> str:
    """Compute the cache key from the given `text`."""
    return md5(text.encode(), usedforsecurity=False).hexdigest()


def cache_time() -> int:
    """Get the Unix time."""
    return int(time())


#
# CRUD
#


def create(key: str, content: str) -> str:
    """Store a HTTP response into a compressed cache file."""
    DIR.mkdir(exist_ok=True, parents=True)
    cache_file(key).write_bytes(compress(f"{cache_time()}|{content}".encode(), level=9))
    return content


def read(key: str) -> str | None:
    """Retreive a response from a potential cache file using the provided `key`."""
    file = cache_file(key)

    with suppress(FileNotFoundError):
        cached_at, content = decompress(file.read_bytes()).decode().split("|", 1)
        elapsed = cache_time() - int(cached_at)
        if 0 <= elapsed < DELAY_BEFORE_EXPIRATION_IN_SEC:
            if APPEND_HEADER:
                bottle.response.headers.append(HEADER_NAME, f"{elapsed / ONE_MINUTE_IN_SEC:,.2f} min")
            return content

        delete(key)

    return None


def delete(key: str) -> None:
    """Delete a cache file."""
    cache_file(key).unlink(missing_ok=True)


#
# The decorator
#


def cache(**cache_kwargs: list[str]) -> Callable:
    """Cache a HTTP response. Decorator to use on routes you want to cache."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: str, **kwargs: str) -> str:
            # No cache when:
            #   - Bottle runs in debug mode
            #   - the HTTP method is not allowed
            if bottle.DEBUG or bottle.request.method not in HTTP_METHODS:
                return func(*args, **kwargs)

            # The cache key is computed from the request path, first
            text = bottle.request.path

            # Then optional request data
            for attr, values in cache_kwargs.items():
                req_attr = getattr(bottle.request, attr)
                for value in values:
                    text += f"-{req_attr.get(value, '')}"

            key = cache_key(text)
            return read(key) or create(key, func(*args, **kwargs))

        return wrapper

    return decorator


__all__ = ("cache",)
