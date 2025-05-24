"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

from unittest.mock import patch

import bottle
from boddle import boddle

import bottle_file_cache


@bottle.route("/hello/<name>")
@bottle_file_cache.cache()
def index(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)


@bottle.route("/hello2/<name>")
@bottle_file_cache.cache(params=["gender", "pron", "not-used"])
def index2(name: str) -> str:
    return bottle.template("<b>Hello {{name}} ({{gender}}, {{pron}})</b>!", name=name, **bottle.request.params)


def cached_files() -> list[str]:
    return [file.name for file in sorted(bottle_file_cache.DIR.glob(f"*.{bottle_file_cache.FILE_EXT}"))]


def test_no_cache_on_debug_mode() -> None:
    assert not cached_files()

    path = "/hello/Alice"
    expected = "<b>Hello Alice</b>!"

    with boddle(url=path), patch.object(bottle, "DEBUG", True):
        # First call is not yet cached
        assert index("Alice") == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one neither
        assert index("Alice") == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

    assert not cached_files()


def test_no_cache_on_disallowed_method() -> None:
    assert not cached_files()

    path = "/hello/Alice"

    with boddle(method="HEAD", url=path):
        # First call is not yet cached
        index("Alice")
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one neither
        index("Alice")
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

    assert not cached_files()


def test_from_path_only() -> None:
    assert not cached_files()

    path = "/hello/Alice"
    expected = "<b>Hello Alice</b>!"

    with boddle(url=path):
        # First call is not yet cached
        assert index("Alice") == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one is cached
        assert index("Alice") == expected
        assert bottle_file_cache.HEADER_NAME in bottle.response.headers

    assert cached_files() == [f"{bottle_file_cache.cache_key(path)}.{bottle_file_cache.FILE_EXT}"]


def test_from_path_and_params() -> None:
    assert not cached_files()

    path = "/hello2/Alice"
    params = {"gender": "female", "pron": "she/her"}
    expected = "<b>Hello Alice (female, she/her)</b>!"

    with boddle(url=path, params=params):
        # First call is not yet cached
        assert index2("Alice") == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one is cached
        assert index2("Alice") == expected
        assert bottle_file_cache.HEADER_NAME in bottle.response.headers

    text = f"{path}-{params['gender']}-{params['pron']}-{params.get('not-used', '')}"
    assert cached_files() == [f"{bottle_file_cache.cache_key(text)}.{bottle_file_cache.FILE_EXT}"]
