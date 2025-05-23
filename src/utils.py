from hashlib import md5


def cache_key(key: str) -> str:
    return md5(key.encode(), usedforsecurity=False).hexdigest()
