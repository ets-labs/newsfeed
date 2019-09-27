"""Application module."""

import asyncio
import os

from aiohttp import web
from dependency_injector import providers

from .containers import Infrastructure, DomainModel, WebApi
from newsfeed.packages import infrastructure


class Application:
    """Application."""

    def __init__(self):
        """Initialize application."""
        self.infrastructure = Infrastructure(
            event_queue=providers.Singleton(
                infrastructure.event_queues.AsyncInMemoryEventQueue,
                **Infrastructure.event_queue.kwargs,
            ),
            event_storage=providers.Singleton(
                infrastructure.event_storage.AsyncInMemoryEventStorage,
                **Infrastructure.event_storage.kwargs,
            ),
            subscription_storage=providers.Singleton(
                infrastructure.subscription_storage.AsyncInMemorySubscriptionStorage,
                **Infrastructure.subscription_storage.kwargs,
            ),
        )
        self.domain_model = DomainModel(infra=self.infrastructure)
        self.web_api = WebApi(domain=self.domain_model)

    def main(self):
        """Run application."""
        web_app = self.web_api.web_app()

        async def event_publishing():
            """Publish events."""
            event_publisher_service = self.domain_model.event_publisher_service()
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
