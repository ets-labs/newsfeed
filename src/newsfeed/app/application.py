"""Application module."""

import asyncio

from aiohttp import web

from .containers import Infrastructure, DomainModel, WebApi


class Application:
    """Application."""

    def __init__(self,
                 infrastructure: Infrastructure,
                 domain_model: DomainModel,
                 web_api: WebApi,
                 processor_concurrency: int):
        """Initialize application."""
        self.infrastructure = infrastructure

        self.domain_model = domain_model
        self.domain_model.infra.override(self.infrastructure)

        self.web_api = web_api
        self.web_api.domain.override(self.domain_model)

        self.processor_concurrency = int(processor_concurrency)
        self.processor_tasks = []

    def main(self):
        """Run application."""
        web_app: web.Application = self.web_api.web_app()

        web_app.on_startup.append(self._start_background_tasks)
        web_app.on_cleanup.append(self._cleanup_background_tasks)

        web.run_app(web_app, port=int(self.web_api.config.port()))

    async def _start_background_tasks(self, _: web.Application):
        loop = asyncio.get_event_loop()

        self.processor_tasks = [
            loop.create_task(self._event_processor_task())
            for _ in range(self.processor_concurrency)
        ]

    async def _cleanup_background_tasks(self, _: web.Application):
        await asyncio.gather(
            *[
                event_processing_task.cancel()
                for event_processing_task in self.processor_tasks
            ]
        )
        self.processor_tasks.clear()

    async def _event_processor_task(self):
        """Process events."""
        event_processor_service = self.domain_model.event_processor_service()
        while True:
            await event_processor_service.process_event()
