"""Main module."""

from aiohttp import web

from .configuration import get_config
from .routes import setup_routes
from .containers import Container


def main():
    container = Container(config=get_config())

    container.configure_logging()
    container.configure_event_loop()

    web_app = container.web_app()
    setup_routes(web_app, container)

    event_processor = container.event_processor_service()

    @web_app.on_startup.append
    async def _on_startup(_: web.Application) -> None:
        event_processor.start_processing()

    @web_app.on_cleanup.append
    async def _on_cleanup(_: web.Application) -> None:
        event_processor.stop_processing()

    container.run_web_app(web_app, print=None)


if __name__ == '__main__':
    main()
