"""Main module."""

from aiohttp import web

from .configuration import get_config
from .containers import Container
from . import webapi


def main():
    container = Container(config=get_config())

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

    web.run_app(web_app, port=int(container.config.webapi.port()))


if __name__ == '__main__':
    main()
