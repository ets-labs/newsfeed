"""Application module."""

from .containers import Infrastructure, DomainModel, WebApi


class Application:
    """Application."""

    def create_web_app(self):
        """Create web application."""
        infrastructure, domain_model, web_api = self.create_containers()

        web_app = web_api.web_app()
        web_app.infrastructure = infrastructure
        web_app.domain_model = domain_model
        web_app.web_api = web_api

        return web_app

    def create_containers(self):
        """Create application containers."""
        # TODO: find out better way of configuring containers
        from dependency_injector import providers
        from newsfeed.packages.infrastructure.event_queues import AsyncInMemoryEventQueue
        from newsfeed.packages.infrastructure.event_storage import AsyncInMemoryEventStorage

        infrastructure = Infrastructure(
            event_queue=providers.Singleton(
                AsyncInMemoryEventQueue,
                **Infrastructure.event_queue.kwargs,
            ),
            event_storage=providers.Singleton(
                AsyncInMemoryEventStorage,
                **Infrastructure.event_storage.kwargs,
            ),
        )
        domain_model = DomainModel(infra=infrastructure)
        web_api = WebApi(domain=domain_model)

        return infrastructure, domain_model, web_api
