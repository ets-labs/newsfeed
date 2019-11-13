"""Application module."""

import asyncio
import logging
from typing import List

from aiohttp import web

from .containers import Infrastructure, DomainModel, WebApi


class Application:
    """Application."""

    def __init__(self,
                 infrastructure: Infrastructure,
                 domain_model: DomainModel,
                 web_api: WebApi):
        """Initialize application."""
        self.infrastructure = infrastructure

        self.domain_model = domain_model
        self.domain_model.infra.override(self.infrastructure)

        self.web_api = web_api
        self.web_api.domain.override(self.domain_model)

        self.processor_tasks: List[asyncio.Task[None]] = []

    def main(self) -> None:
        """Run application."""
        web_app: web.Application = self.web_api.web_app()

        web_app.on_startup.append(self._start_background_tasks)
        web_app.on_cleanup.append(self._cleanup_background_tasks)
        logging.basicConfig(level=logging.DEBUG)
        web.run_app(web_app, port=int(self.web_api.config.port()))

    async def _start_background_tasks(self, _: web.Application) -> None:
        loop = asyncio.get_event_loop()

        self.processor_tasks = [
            loop.create_task(self._event_processor_task())
            for _ in range(int(self.domain_model.config.processor_concurrency()))
        ]

    async def _cleanup_background_tasks(self, _: web.Application) -> None:
        for event_processing_task in self.processor_tasks:
            event_processing_task.cancel()
        self.processor_tasks.clear()

    async def _event_processor_task(self) -> None:
        """Process events."""
        event_processor_service = self.domain_model.event_processor_service()
        while True:
            await event_processor_service.process_event()
