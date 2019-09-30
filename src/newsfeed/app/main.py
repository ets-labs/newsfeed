"""Main module."""

import asyncio
import os

from aiohttp import web

from .factory import application_factory
from .application import Application


def main(application: Application):
    """Run application."""
    web_app = application.web_api.web_app()

    async def event_publishing():
        """Publish events."""
        event_publisher_service = application.domain_model.event_publisher_service()
        while True:
            await event_publisher_service.process_event()

    @web_app.on_startup.append
    async def start_background_tasks(_):
        """Start application background tasks."""
        loop = asyncio.get_event_loop()
        web_app['event_publishing'] = loop.create_task(event_publishing())

    @web_app.on_cleanup.append
    async def cleanup_background_tasks(_):
        """Stop application background tasks."""
        web_app['event_publishing'].cancel()
        await web_app['event_publishing']

    web.run_app(web_app, port=int(os.getenv('PORT')))


if __name__ == '__main__':
    application = application_factory()
    main(application)
