"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

from unittest.mock import patch

import bottle
from boddle import boddle

import bottle_file_cache
from bottle_file_cache import cache


@bottle.route("/hello/<name>")
@cache()
def index(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)


@bottle.route("/hello2/<name>")
@cache(params=["gender", "pron", "not-used"])
def index2(name: str) -> str:
    return bottle.template("<b>Hello {{name}} ({{gender}}, {{pron}})</b>!", name=name, **bottle.request.params)


WHOAMI = "Alice"


def cached_files() -> list[str]:
    return [file.name for file in sorted(bottle_file_cache.DIR.glob(f"*.{bottle_file_cache.FILE_EXT}"))]


def test_no_cache_on_debug_mode() -> None:
    assert not cached_files()

    path = f"/hello/{WHOAMI}"
    expected = f"<b>Hello {WHOAMI}</b>!"

    with boddle(url=path), patch.object(bottle, "DEBUG", True):
        # First call is not yet cached
        assert index(WHOAMI) == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one neither
        assert index(WHOAMI) == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

    assert not cached_files()


def test_no_cache_on_disallowed_method() -> None:
    assert not cached_files()

    path = f"/hello/{WHOAMI}"

    with boddle(method="HEAD", url=path):
        # First call is not yet cached
        index(WHOAMI)
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one neither
        index(WHOAMI)
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

    assert not cached_files()


def test_from_path_only() -> None:
    assert not cached_files()

    path = f"/hello/{WHOAMI}"
    expected = f"<b>Hello {WHOAMI}</b>!"

    with boddle(url=path):
        # First call is not yet cached
        assert index(WHOAMI) == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one is cached
        assert index(WHOAMI) == expected
        assert bottle_file_cache.HEADER_NAME in bottle.response.headers

    assert cached_files() == [f"{bottle_file_cache.cache_key(path)}.{bottle_file_cache.FILE_EXT}"]


def test_from_path_and_params() -> None:
    assert not cached_files()

    path = f"/hello2/{WHOAMI}"
    params = {"gender": "female", "pron": "she/her"}
    expected = f"<b>Hello {WHOAMI} (female, she/her)</b>!"

    with boddle(url=path, params=params, headers={}):
        # First call is not yet cached
        assert index2(WHOAMI) == expected
        assert bottle_file_cache.HEADER_NAME not in bottle.response.headers

        # Second one is cached
        assert index2(WHOAMI) == expected
        assert bottle_file_cache.HEADER_NAME in bottle.response.headers

    text = f"{path}-{params['gender']}-{params['pron']}-{params.get('not-used', '')}"
    assert cached_files() == [f"{bottle_file_cache.cache_key(text)}.{bottle_file_cache.FILE_EXT}"]
