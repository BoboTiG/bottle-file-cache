"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

import atexit
from contextlib import suppress
from functools import wraps
from hashlib import md5
from pathlib import Path
from tempfile import TemporaryDirectory
from time import time
from types import SimpleNamespace
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
# Configuration
#
_TMP = TemporaryDirectory(prefix="bottle-file-", suffix="-cache", ignore_cleanup_errors=True)
atexit.register(_TMP.cleanup)

CONFIG = SimpleNamespace(
    folder=Path(_TMP.name),
    file_ext="cache",
    expiration_in_sec=10 * 60,
    append_header=True,
    header_name="Cached-Since",
    http_methods=["GET"],
)
ONE_MINUTE_IN_SEC = 60


#
# Utilities
#


def compute_key(text: str) -> str:
    """Compute the cache key from the given `text`."""
    return md5(text.encode(), usedforsecurity=False).hexdigest()


def get_file(key: str) -> Path:
    """Get the cache file from the given `key`."""
    return CONFIG.folder / f"{key}.{CONFIG.file_ext}"


def get_time() -> int:
    """Get the Unix time."""
    return int(time())


#
# CRUD
#


def create(key: str, content: str) -> str:
    """Store a HTTP response into a compressed cache file."""
    CONFIG.folder.mkdir(exist_ok=True, parents=True)
    get_file(key).write_bytes(compress(f"{get_time()}|{content}".encode(), level=9))
    return content


def read(key: str) -> str | None:
    """Retreive a response from a potential cache file using the provided `key`."""
    file = get_file(key)

    with suppress(FileNotFoundError):
        cached_at, content = decompress(file.read_bytes()).decode().split("|", 1)
        elapsed = get_time() - int(cached_at)
        if 0 <= elapsed < CONFIG.expiration_in_sec:
            if CONFIG.append_header:
                bottle.response.headers.append(CONFIG.header_name, f"{elapsed / ONE_MINUTE_IN_SEC:,.2f} min")
            return content

        delete(key)

    return None


def delete(key: str) -> None:
    """Delete a cache file."""
    get_file(key).unlink(missing_ok=True)


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
            if bottle.DEBUG or bottle.request.method not in CONFIG.http_methods:
                return func(*args, **kwargs)

            # The cache key is computed from the request path, first
            text = bottle.request.path

            # Then optional request data
            for attr, values in cache_kwargs.items():
                req_attr = getattr(bottle.request, attr)
                for value in values:
                    text += f"-{req_attr.get(value, '')}"

            key = compute_key(text)
            return read(key) or create(key, func(*args, **kwargs))

        return wrapper

    return decorator


__all__ = ("cache",)
