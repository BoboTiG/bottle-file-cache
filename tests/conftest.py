"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from pathlib import Path

import pytest

import bottle_file_cache


@pytest.fixture(autouse=True)
def isolate(tmp_path: Path) -> None:
    bottle_file_cache.CONFIG.folder = tmp_path
