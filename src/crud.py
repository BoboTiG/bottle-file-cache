
from contextlib import suppress
from time import monotonic
from zlib import compress, decompress
from src import constants, utils

import bottle


def create(key: str, value: str) -> str:
    """Store a HTTP response into a compressed cache file."""
    file = constants.FILES_CACHE / f"{key}.cache"
    data = f"{int(monotonic())}|{value}".encode()
    file.write_bytes(compress(data, level=9))
    return value


def read(key: str) -> str | None:
    """Retreive a response from a potential cache file."""
    file = constants.FILES_CACHE / f"{key}.cache"

    with suppress(FileNotFoundError):
        when, page = decompress(file.read_bytes()).decode().split("|", 1)
        if (diff := int(monotonic()) - int(when)) < constants.DELAY_BEFORE_EXPIRATION_IN_SEC:
            if constants.ADD_HEADER:
                bottle.response.headers.append(constants.HEADER_NAME, f"{diff / constants.ONE_MINUTE_IN_SEC:0.2f} min")
            return page

        delete(key)

    return None


def delete(key: str) -> None:
    (constants.FILES_CACHE / utils.cache_key(key)).unlink(missing_ok=True)
