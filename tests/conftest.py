"""Application test fixtures."""

from pytest import fixture
from dependency_injector import containers, providers

from newsfeed.application import Application
from newsfeed import infrastructure


class TestInfrastructure(containers.DeclarativeContainer):
    """Test infrastructure container."""

    config = providers.Configuration('infrastructure')

    event_queue = providers.Singleton(
        infrastructure.event_queues.InMemoryEventQueue,
        config=config.event_queue,
    )

    event_storage = providers.Singleton(
        infrastructure.event_storages.InMemoryEventStorage,
        config=config.event_storage,
    )

    subscription_storage = providers.Singleton(
        infrastructure.subscription_storages.InMemorySubscriptionStorage,
        config=config.subscription_storage,
    )


class TestApplication(Application):
    """Test application."""

    class Containers(Application.Containers):
        """Application containers."""

        infrastructure = TestInfrastructure


@fixture
def app():
    """Create test application."""
    return TestApplication(
        config={
            'infrastructure': {
                'event_queue': {
                    'max_size': 1,
                },
                'event_storage': {
                    'max_newsfeeds': 3,
                    'max_events_per_newsfeed': 5,
                },
                'subscription_storage': {
                    'max_newsfeeds': 3,
                    'max_subscriptions_per_newsfeed': 5,
                },
            },
            'domain_model': {
                'newsfeed_id_length': 16,
                'processor_concurrency': 1,
            },
            'web_api': {
                'base_path': '/',
            },
        },
    )


@fixture
def web_app(app):
    """Create test web application."""
    return app.web_api.web_app()


@fixture
async def web_client(aiohttp_client, web_app):
    """Create test application client."""
    return await aiohttp_client(web_app)
