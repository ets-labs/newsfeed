"""Containers module."""

from dependency_injector import containers, providers

from newsfeed.packages import infrastructure, domain_model, webapi


class Infrastructure(containers.DeclarativeContainer):
    """Infrastructure container."""

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


class DomainModel(containers.DeclarativeContainer):
    """Domain model container."""

    config = providers.Configuration('domain_model')

    infra: Infrastructure = providers.DependenciesContainer()

    # Common

    newsfeed_id_specification = providers.Singleton(
        domain_model.newsfeed_id.NewsfeedIDSpecification,
        max_length=config.newsfeed_id_length,
    )

    # Subscription

    subscription_factory = providers.Factory(
        domain_model.subscription.SubscriptionFactory,
        cls=domain_model.subscription.Subscription,
    )

    subscription_specification = providers.Singleton(
        domain_model.subscription.SubscriptionSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    subscription_repository = providers.Singleton(
        domain_model.subscription.SubscriptionRepository,
        factory=subscription_factory,
        storage=infra.subscription_storage,
    )

    subscription_service = providers.Singleton(
        domain_model.subscription.SubscriptionService,
        factory=subscription_factory,
        specification=subscription_specification,
        repository=subscription_repository,
    )

    # Event

    event_factory = providers.Factory(
        domain_model.event.EventFactory,
        cls=domain_model.event.Event,
    )

    event_specification = providers.Singleton(
        domain_model.event.EventSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    event_repository = providers.Singleton(
        domain_model.event.EventRepository,
        factory=event_factory,
        storage=infra.event_storage,
    )

    event_dispatcher_service = providers.Singleton(
        domain_model.event_dispatcher.EventDispatcherService,
        event_factory=event_factory,
        event_specification=event_specification,
        event_queue=infra.event_queue,
    )

    event_processor_service = providers.Singleton(
        domain_model.event_processor.EventProcessorService,
        event_queue=infra.event_queue,
        event_factory=event_factory,
        event_repository=event_repository,
        subscription_repository=subscription_repository,
    )


class WebApi(containers.DeclarativeContainer):
    """Web API container."""

    config = providers.Configuration('web_api')

    domain: DomainModel = providers.DependenciesContainer()

    web_app = providers.Factory(
        webapi.app.create_web_app,
        base_path=config.base_path,
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
            webapi.app.route(
                method='GET',
                path='/newsfeed/{newsfeed_id}/subscribers/subscriptions/',
                handler=providers.Coroutine(
                    webapi.handlers.subscriptions.get_subscriber_subscriptions_handler,
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
            webapi.app.route(
                method='DELETE',
                path='/newsfeed/{newsfeed_id}/events/{event_id}/',
                handler=providers.Coroutine(
                    webapi.handlers.events.delete_event_handler,
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
                    base_path=config.base_path,
                ),
            ),
        ],
    )
