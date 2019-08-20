"""Containers module."""

from dependency_injector import containers, providers

from newsfeed.packages import infrastructure, domain_model, webapi


class Infrastructure(containers.DeclarativeContainer):
    """Infrastructure container."""

    config = providers.Configuration('infrastructure')

    event_queue = providers.Singleton(
        infrastructure.event_queues.EventQueue,
        config=config.event_queue,
    )

    event_storage = providers.Singleton(
        infrastructure.event_storage.EventStorage,
        config=config.event_storage,
    )

    subscription_storage = providers.Singleton(
        infrastructure.subscription_storage.SubscriptionStorage,
        config=config.subscription_storage,
    )


class DomainModel(containers.DeclarativeContainer):
    """Domain model container."""


class WebApi(containers.DeclarativeContainer):
    """Web API container."""

    domain: DomainModel = providers.DependenciesContainer()

    web_app = providers.Factory(
        webapi.app.create_web_app,
        routes=[
            # Miscellaneous
            webapi.app.route(
                method='GET',
                path='/status/',
                handler=providers.Coroutine(
                    webapi.handlers.misc.get_status_handler,
                ),
            ),
        ],
    )
