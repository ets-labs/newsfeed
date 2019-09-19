"""Main module."""

import asyncio
import os

from aiohttp import web

from .application import Application


async def event_publishing(domain_model):
    """Publish events."""
    event_publisher_service = domain_model.event_publisher_service()
    while True:
        await event_publisher_service.process_event()


def main():
    """Run application."""
    app = Application()

    web_app = app.web_api.web_app()

    @web_app.on_startup.append
    async def start_background_tasks(web_app: web.Application):
        """Start application background tasks."""
        loop = asyncio.get_event_loop()
        web_app['event_publishing'] = loop.create_task(event_publishing(app.domain_model))

    @web_app.on_cleanup.append
    async def cleanup_background_tasks(web_app: web.Application):
        """Stop application background tasks."""
        web_app['event_publishing'].cancel()
        await web_app['event_publishing']

    web.run_app(web_app, port=int(os.getenv('PORT')))


if __name__ == '__main__':
    main()
