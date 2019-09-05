"""Main module."""

import asyncio
import os

from aiohttp import web

from .application import Application


async def event_publishing(web_app):
    """Publish events."""
    event_publisher_service = web_app.domain_model.event_publisher_service()
    while True:
        await event_publisher_service.process_event()


async def start_background_tasks(web_app: web.Application):
    """Start application background tasks."""
    loop = asyncio.get_event_loop()
    web_app['event_publishing'] = loop.create_task(event_publishing(web_app))


async def cleanup_background_tasks(app):
    """Stop application background tasks."""
    app['event_publishing'].cancel()
    await app['event_publishing']


def main():
    """Run application."""
    app = Application()

    web_app = app.create_web_app()

    web_app.on_startup.append(start_background_tasks)
    web_app.on_cleanup.append(cleanup_background_tasks)

    web.run_app(web_app, port=int(os.getenv('PORT')))


if __name__ == '__main__':
    main()
