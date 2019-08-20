"""Web API module."""

from aiohttp import web


def create_web_app(*, routes) -> web.Application:
    """Create web application."""
    app = web.Application()
    app.add_routes(routes)
    return app


route = web.route
