"""Containers module."""

from dependency_injector import containers, providers

from newsfeed.packages import infrastructure, domain_model, webapi


class Infrastructure(containers.DeclarativeContainer):
    """Infrastructure container."""

    config = providers.Configuration('infrastructure')

    event_queue = providers.Singleton(
        infrastructure.event_queues.AsyncInMemoryEventQueue,
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


class DomainModel(containers.DeclarativeContainer):
    """Domain model container."""

    infra: Infrastructure = providers.DependenciesContainer()

    # Subscription

    subscription_factory = providers.Factory(
        domain_model.subscriptions.SubscriptionFactory,
        cls=domain_model.subscriptions.Subscription,
    )

    subscription_specification = providers.Singleton(
        domain_model.subscriptions.SubscriptionSpecification,
    )

    subscription_repository = providers.Singleton(
        domain_model.subscriptions.SubscriptionRepository,
        factory=subscription_factory,
        storage=infra.subscription_storage,
    )

    subscription_service = providers.Singleton(
        domain_model.subscriptions.SubscriptionService,
        factory=subscription_factory,
        specification=subscription_specification,
        repository=subscription_repository,
    )

    # Event

    event_factory = providers.Factory(
        domain_model.events.EventFactory,
        cls=domain_model.events.Event,
    )

    event_specification = providers.Singleton(domain_model.events.EventSpecification)

    event_repository = providers.Singleton(
        domain_model.events.EventRepository,
        factory=event_factory,
        storage=infra.event_storage,
    )

    event_dispatcher_service = providers.Singleton(
        domain_model.events.EventDispatcherService,
        factory=event_factory,
        specification=event_specification,
        queue=infra.event_queue,
    )

    event_publisher_service = providers.Singleton(
        domain_model.events.EventPublisherService,
        event_queue=infra.event_queue,
        event_factory=event_factory,
        event_repository=event_repository,
        subscription_repository=subscription_repository,
    )


class WebApi(containers.DeclarativeContainer):
    """Web API container."""

    domain: DomainModel = providers.DependenciesContainer()

    web_app = providers.Factory(
        webapi.app.create_web_app,
        routes=[
            # Subscriptions
            webapi.app.route(
                method='GET',
                path='/newsfeed/{newsfeed_id}/subscriptions/',
                handler=providers.Coroutine(
                    webapi.handlers.subscriptions.get_subscriptions_handler,
                    subscription_service=domain.subscription_service,
                ),
            ),
            webapi.app.route(
                method='POST',
                path='/newsfeed/{newsfeed_id}/subscriptions/',
                handler=providers.Coroutine(
                    webapi.handlers.subscriptions.post_subscription_handler,
                    subscription_service=domain.subscription_service,
                ),
            ),
            webapi.app.route(
                method='DELETE',
                path='/newsfeed/{newsfeed_id}/subscriptions/{subscription_id}/',
                handler=providers.Coroutine(
                    webapi.handlers.subscriptions.delete_subscription_handler,
                    subscription_service=domain.subscription_service,
                ),
            ),

            # Events
            webapi.app.route(
                method='GET',
                path='/newsfeed/{newsfeed_id}/events/',
                handler=providers.Coroutine(
                    webapi.handlers.events.get_events_handler,
                    event_repository=domain.event_repository,
                ),
            ),
            webapi.app.route(
                method='POST',
                path='/newsfeed/{newsfeed_id}/events/',
                handler=providers.Coroutine(
                    webapi.handlers.events.post_event_handler,
                    event_dispatcher_service=domain.event_dispatcher_service,
                ),
            ),

            # Miscellaneous
            webapi.app.route(
                method='GET',
                path='/status/',
                handler=providers.Coroutine(
                    webapi.handlers.misc.get_status_handler,
                ),
            ),
            webapi.app.route(
                method='GET',
                path='/docs/',
                handler=providers.Coroutine(
                    webapi.handlers.misc.get_openapi_schema_handler,
                ),
            ),
        ],
    )
