"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

from __future__ import annotations

from time import sleep
from unittest.mock import patch

import bottle
import pytest
from webtest import TestApp

import bottle_file_cache

from . import server


@pytest.fixture(scope="session")
def app() -> TestApp:
    return TestApp(server.app)


WHOAMI = "Alice"


def cached_files() -> list[str]:
    return [
        file.name for file in sorted(bottle_file_cache.CONFIG.folder.glob(f"*.{bottle_file_cache.CONFIG.file_ext}"))
    ]


def test_no_cache_on_debug_mode(app: TestApp) -> None:
    path = f"/hello/{WHOAMI}"
    expected = f"<b>Hello {WHOAMI}</b>!".encode()

    with patch.object(bottle, "DEBUG", new=True):
        # First call is not yet cached
        response = app.get(path)
        assert response.body == expected
        assert bottle_file_cache.CONFIG.header_name not in response.headers

        # Second one neither
        response = app.get(path)
        assert response.body == expected
        assert bottle_file_cache.CONFIG.header_name not in response.headers

    assert not cached_files()


def test_no_cache_on_disallowed_method(app: TestApp) -> None:
    path = f"/hello/{WHOAMI}"

    # First call is not yet cached
    response = app.head(path)
    assert bottle_file_cache.CONFIG.header_name not in response.headers

    # Second one neither
    response = app.head(path)
    assert bottle_file_cache.CONFIG.header_name not in response.headers

    assert not cached_files()


def test_from_path_only(app: TestApp) -> None:
    path = f"/hello/{WHOAMI}"
    expected = f"<b>Hello {WHOAMI}</b>!".encode()

    # First call is not yet cached
    response = app.get(path)
    assert response.body == expected
    assert bottle_file_cache.CONFIG.header_name not in response.headers

    # Second one is cached
    response = app.get(path)
    assert response.body == expected
    assert bottle_file_cache.CONFIG.header_name in response.headers

    assert cached_files() == [f"{bottle_file_cache.compute_key(path)}.{bottle_file_cache.CONFIG.file_ext}"]


def test_from_path_and_params(app: TestApp) -> None:
    path = f"/hello2/{WHOAMI}"
    params = {"gender": "female", "pron": "she/her"}
    expected = f"<b>Hello {WHOAMI} (female, she/her)</b>!".encode()

    # First call is not yet cached
    response = app.get(path, params=params)
    assert response.body == expected
    assert bottle_file_cache.CONFIG.header_name not in response.headers

    # Second one is cached
    response = app.get(path, params=params)
    assert response.body == expected
    assert bottle_file_cache.CONFIG.header_name in response.headers

    text = f"{path}-{params['gender']}-{params['pron']}-{params.get('not-used', '')}"
    assert cached_files() == [f"{bottle_file_cache.compute_key(text)}.{bottle_file_cache.CONFIG.file_ext}"]


def test_expires(app: TestApp) -> None:
    path = f"/hello3/{WHOAMI}"
    expected = f"<b>Hello {WHOAMI}</b>!".encode()

    # First call is not yet cached
    response = app.get(path)
    assert response.body == expected
    assert bottle_file_cache.CONFIG.header_name not in response.headers
    assert len(cached_files()) == 1

    sleep(1.01)

    # Second one is not cached (expired too soon)
    response = app.get(path)
    assert response.body == expected
    assert bottle_file_cache.CONFIG.header_name not in response.headers
