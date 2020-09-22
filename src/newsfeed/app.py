"""Application module."""

from aiohttp import web

from .containers import Container
from .routes import setup_routes
from . import handlers


def create_app() -> web.Application:
    container = Container()

    container.config.from_yaml('config/newsfeed.yml')
    container.config.from_yaml('config/newsfeed.local.yml')
    container.config.logging.from_yaml('config/logging.yml')
    container.config.logging.from_yaml('config/logging.local.yml')

    container.configure_logging()
    container.configure_event_loop()

    container.wire(packages=[handlers])

    app = web.Application()
    app.container = container
    setup_routes(app)

    event_processor = container.event_processor_service()

    @app.on_startup.append
    async def _on_startup(_: web.Application) -> None:
        event_processor.start_processing()

    @app.on_cleanup.append
    async def _on_cleanup(_: web.Application) -> None:
        event_processor.stop_processing()

    return app
