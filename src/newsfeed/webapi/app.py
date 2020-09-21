"""Application module."""

from aiohttp import web

from .routes import setup_routes


def create_app() -> web.Application:
    app = web.Application()
    setup_routes(app)
    return app
