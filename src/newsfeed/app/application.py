"""Application module."""

import asyncio

from aiohttp import web

from .containers import Infrastructure, DomainModel, WebApi


class Application:
    """Application."""

    def __init__(self, infrastructure: Infrastructure, domain_model: DomainModel, web_api: WebApi):
        """Initialize application."""
        self.infrastructure = infrastructure

        self.domain_model = domain_model
        self.domain_model.infra.override(self.infrastructure)

        self.web_api = web_api
        self.web_api.domain.override(self.domain_model)

    def main(self):
        """Run application."""
        web_app: web.Application = self.web_api.web_app()

        web_app.on_startup.append(self._start_background_tasks)
        web_app.on_cleanup.append(self._cleanup_background_tasks)

        web.run_app(web_app, port=int(self.web_api.config.port()))

    async def _start_background_tasks(self, web_app: web.Application):
        loop = asyncio.get_event_loop()
        web_app['event_processing'] = loop.create_task(self._event_processing_task())

    async def _cleanup_background_tasks(self, web_app: web.Application):
        web_app['event_processing'].cancel()
        await web_app['event_processing']

    async def _event_processing_task(self):
        """Process events."""
        event_processor_service = self.domain_model.event_processor_service()
        while True:
            await event_processor_service.process_event()
