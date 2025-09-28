"""Simple file cache for the Python Bottle web framework.

You can always get the latest version at:
    https://github.com/BoboTiG/bottle-file-cache
"""

import bottle

from bottle_file_cache import cache


@bottle.route("/hello/<name>")
@cache()
def index(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)


@bottle.route("/hello2/<name>")
@cache(params=["gender", "pron", "not-used"])
def index2(name: str) -> str:
    return bottle.template("<b>Hello {{name}} ({{gender}}, {{pron}})</b>!", name=name, **bottle.request.params)


@bottle.route("/hello3/<name>")
@cache(expires=1)
def index3(name: str) -> str:
    return bottle.template("<b>Hello {{name}}</b>!", name=name)


app = bottle.default_app()
