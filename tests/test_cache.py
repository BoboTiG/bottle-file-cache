"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

import time
from unittest.mock import patch

import bottle_file_cache

KEY = bottle_file_cache.cache_key("something")


def cached_files() -> list[str]:
    return [file.name for file in sorted(bottle_file_cache.DIR.glob(f"*.{bottle_file_cache.FILE_EXT}"))]


def test_create() -> None:
    assert not cached_files()

    value = "data"
    assert bottle_file_cache.create(KEY, value) == value
    assert cached_files() == [f"{KEY}.{bottle_file_cache.FILE_EXT}"]


def test_read_no_cache_entry() -> None:
    assert not cached_files()

    assert bottle_file_cache.read(KEY) is None


def test_read_empty_string() -> None:
    assert not cached_files()

    value = ""
    bottle_file_cache.create(KEY, value)
    assert bottle_file_cache.read(KEY) == value


def test_read_expired() -> None:
    assert not cached_files()

    value = "data"
    bottle_file_cache.create(KEY, value)
    assert cached_files()

    assert bottle_file_cache.read(KEY) == value

    with patch.object(bottle_file_cache, "DELAY_BEFORE_EXPIRATION_IN_SEC", new=1):
        time.sleep(1.01)
        assert bottle_file_cache.read(KEY) is None

    assert not cached_files()


def test_delete() -> None:
    assert not cached_files()

    bottle_file_cache.create(KEY, "data")
    bottle_file_cache.delete(KEY)
    bottle_file_cache.delete(KEY)  # Should not fail

    assert not cached_files()
