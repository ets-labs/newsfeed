"""Web API module."""

from typing import Sequence

from aiohttp import web


def create_web_app(*, base_path: str, routes: Sequence[web.RouteDef]) -> web.Application:
    """Create web application."""
    app = web.Application()

    if base_path.endswith('/'):
        base_path = base_path[:-1]

    prefixed_routes = []
    for base_route in routes:
        prefixed_routes.append(
            web.route(
                method=base_route.method,
                path=f'{base_path}{base_route.path}',
                handler=base_route.handler,
                **base_route.kwargs,
            )
        )
    app.add_routes(prefixed_routes)

    return app


route = web.route
