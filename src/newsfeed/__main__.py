"""Main module."""

from aiohttp import web

from .containers import Container
from . import webapi


def main() -> None:
    container = Container()

    container.config.from_yaml('config/newsfeed.yml')
    container.config.from_yaml('config/newsfeed.local.yml')
    container.config.logging.from_yaml('config/logging.yml')
    container.config.logging.from_yaml('config/logging.local.yml')

    container.configure_logging()
    container.configure_event_loop()

    container.wire(packages=[webapi])

    web_app = webapi.app.create_app()
    event_processor = container.event_processor_service()

    @web_app.on_startup.append
    async def _on_startup(_: web.Application) -> None:
        event_processor.start_processing()

    @web_app.on_cleanup.append
    async def _on_cleanup(_: web.Application) -> None:
        event_processor.stop_processing()

    web.run_app(
        web_app,
        port=int(container.config.webapi.port()),
        print=lambda *_: None,
    )


if __name__ == '__main__':
    main()
