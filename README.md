# Bottle File Cache

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

TODO.
