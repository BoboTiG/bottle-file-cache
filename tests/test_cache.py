"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

import shutil
import time
from typing import TYPE_CHECKING
from unittest.mock import patch

import bottle_file_cache

if TYPE_CHECKING:
    from pathlib import Path

KEY = bottle_file_cache.compute_key("something")


def cached_files() -> list[str]:
    return [
        file.name for file in sorted(bottle_file_cache.CONFIG.folder.glob(f"*.{bottle_file_cache.CONFIG.file_ext}"))
    ]


def test_create() -> None:
    assert not cached_files()

    value = "data"
    assert bottle_file_cache.create(KEY, value) == value
    assert cached_files() == [f"{KEY}.{bottle_file_cache.CONFIG.file_ext}"]


def test_create_retries_when_cache_dir_vanishes_before_write() -> None:
    original_mkdir = bottle_file_cache.CONFIG.folder.__class__.mkdir
    removed_once = False

    def mkdir_then_remove(self: Path, *args: Path, **kwargs: bool) -> None:
        nonlocal removed_once

        if not removed_once:
            # Simulate an external deletion of the folder right before write_bytes()
            removed_once = True
            shutil.rmtree(bottle_file_cache.CONFIG.folder, ignore_errors=True)
        else:
            original_mkdir(self, *args, **kwargs)

    with patch.object(bottle_file_cache.CONFIG.folder.__class__, "mkdir", mkdir_then_remove):
        result = bottle_file_cache.create("93f2de3a312a2dd4a08cc5c535bfff98", "<html>cached</html>")

    assert result == "<html>cached</html>"
    assert bottle_file_cache.get_file("93f2de3a312a2dd4a08cc5c535bfff98").exists()


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

    with patch.object(bottle_file_cache.CONFIG, "expiration_in_sec", new=1):
        time.sleep(1.01)
        assert bottle_file_cache.read(KEY) is None

    assert not cached_files()


def test_read_expires() -> None:
    assert not cached_files()

    value = "data"
    bottle_file_cache.create(KEY, value)
    assert cached_files()

    assert bottle_file_cache.read(KEY) == value

    time.sleep(1.01)
    assert bottle_file_cache.read(KEY, expires=1) is None

    assert not cached_files()


def test_read_expiration_uses_configured_ttl_when_expires_is_zero() -> None:
    with patch.object(bottle_file_cache, "get_time", lambda: 1000):
        bottle_file_cache.create("k1", "payload")

    with patch.object(bottle_file_cache, "get_time", lambda: 1010):
        assert bottle_file_cache.read("k1", expires=0) == "payload"


def test_delete() -> None:
    assert not cached_files()

    bottle_file_cache.create(KEY, "data")
    bottle_file_cache.delete(KEY)
    bottle_file_cache.delete(KEY)  # Should not fail

    assert not cached_files()
