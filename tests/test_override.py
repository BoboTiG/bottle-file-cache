"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

import bottle_file_cache


def my_cache_key(text: str) -> str:
    return text[::-1]


bottle_file_cache.cache_key = my_cache_key


def test_cache_key_override() -> None:
    assert bottle_file_cache.cache_key("text") == "txet"
