# Bottle File Cache

[![PyPI version](https://badge.fury.io/py/bottle-file-cache.svg)](https://badge.fury.io/py/bottle-file-cache)
[![Python versions](https://img.shields.io/pypi/pyversions/bottle-file-cache.svg)](https://pypi.python.org/pypi/bottle-file-cache)

A simple file cache for the Python [Bottle](https://pypi.org/project/bottle) web framework.

## Installation

```bash
python -m pip install -U bottle-file-cache
```

## Usage

Given that example:

```python
import bottle


@bottle.route("/hello/<name>")
def index(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)


if __name__ == "__main__":
    bottle.run(host="localhost", port=8080)
```

Add those lines to enable the cache:

```diff
+from bottle_file_cache import cache
import bottle


@bottle.route("/hello/<name>")
+@cache()
def index(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)
```

And that's it!

## Advanced Usage

### Bottle Parameters

You can specify more details to compute the cache key.

Here, it takes URL parameters in addition to the request path:

```python
@bottle.route("/hello2/<name>")
@cache(params=["gender", "pron", "not-used"])
def index2(name: str) -> str:
    return bottle.template("<b>Hello {{name}} ({{gender}}, {{pron}})</b>!", name=name, **bottle.request.params)
```

### Par-Call Expiration

You can specify a custom expiration time (in seconds) on a per-call basis:

```python
@bottle.route("/hello3/<name>")
@cache(expires=1)
def index3(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)
```
