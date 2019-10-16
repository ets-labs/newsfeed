"""Application test fixtures."""

from pytest import fixture
from dependency_injector import containers, providers

from newsfeed.app.factory import application_factory
from newsfeed.app.containers import WebApi
from newsfeed.packages import infrastructure


class TestInfrastructure(containers.DeclarativeContainer):
    """Infrastructure container."""

    config = providers.Configuration('infrastructure')

    event_queue = providers.Singleton(
        infrastructure.event_queues.InMemoryEventQueue,
        config=config.event_queue,
    )

    event_storage = providers.Singleton(
        infrastructure.event_storage.AsyncInMemoryEventStorage,
        config=config.event_storage,
    )

    subscription_storage = providers.Singleton(
        infrastructure.subscription_storage.AsyncInMemorySubscriptionStorage,
        config=config.subscription_storage,
    )


@fixture
def app():
    """Create test application."""
    return application_factory(
        infrastructure=TestInfrastructure(),
        web_api=WebApi(
            config={
                'base_path': '/',
            },
        )
    )


@fixture
def web_app(app):
    """Create test web application."""
    return app.web_api.web_app()


@fixture
async def web_client(aiohttp_client, web_app):
    """Create test application client."""
    return await aiohttp_client(web_app)
