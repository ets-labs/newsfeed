"""Application module."""

import os

from .containers import Infrastructure, DomainModel, WebApi


def create_infrastructure_container(config):
    # TODO: find out better way of configuring containers
    from dependency_injector import providers
    from newsfeed.packages.infrastructure.event_queues import AsyncInMemoryEventQueue
    from newsfeed.packages.infrastructure.event_storage import AsyncInMemoryEventStorage
    from newsfeed.packages.infrastructure.subscription_storage import \
        AsyncInMemorySubscriptionStorage  # noqa

    return Infrastructure(
        event_queue=providers.Singleton(
            AsyncInMemoryEventQueue,
            **Infrastructure.event_queue.kwargs,
        ),
        event_storage=providers.Singleton(
            AsyncInMemoryEventStorage,
            **Infrastructure.event_storage.kwargs,
        ),
        subscription_storage=providers.Singleton(
            AsyncInMemorySubscriptionStorage,
            **Infrastructure.subscription_storage.kwargs,
        ),
    )


class Application:
    """Application."""

    infrastructure = create_infrastructure_container(os.environ)

    domain_model = DomainModel(infra=infrastructure)

    web_api = WebApi(domain=domain_model)
