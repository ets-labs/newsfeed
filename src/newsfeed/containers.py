"""Containers module."""

from dependency_injector import containers, providers

from newsfeed import core, infrastructure, domain


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    configure_logging = providers.Callable(
        core.log.configure_logging,
        level=config.log_level,
    )

    configure_event_loop = providers.Callable(
        core.loop.configure_event_loop,
        enable_uvloop=config.enable_uvloop,
    )

    # Infrastructure

    event_queue = providers.Singleton(
        infrastructure.event_queues.InMemoryEventQueue,
        config=config.infrastructure.event_queue,
    )

    event_storage = providers.Singleton(
        infrastructure.event_storages.InMemoryEventStorage,
        config=config.infrastructure.event_storage,
    )

    subscription_storage = providers.Singleton(
        infrastructure.subscription_storages.InMemorySubscriptionStorage,
        config=config.infrastructure.subscription_storage,
    )

    # Domain model

    newsfeed_id_specification = providers.Singleton(
        domain.newsfeed_id.NewsfeedIDSpecification,
        max_length=config.domain.newsfeed_id_length,
    )

    # Domain model -> Subscriptions

    subscription_factory = providers.Factory(domain.subscription.SubscriptionFactory)

    subscription_specification = providers.Singleton(
        domain.subscription.SubscriptionSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    subscription_repository = providers.Singleton(
        domain.subscription.SubscriptionRepository,
        factory=subscription_factory,
        storage=subscription_storage,
    )

    subscription_service = providers.Singleton(
        domain.subscription.SubscriptionService,
        factory=subscription_factory,
        specification=subscription_specification,
        repository=subscription_repository,
    )

    # Domain model -> Events

    event_factory = providers.Factory(domain.event.EventFactory)

    event_specification = providers.Singleton(
        domain.event.EventSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    event_repository = providers.Singleton(
        domain.event.EventRepository,
        factory=event_factory,
        storage=event_storage,
    )

    # Domain model -> Services

    event_dispatcher_service = providers.Factory(
        domain.event_dispatcher.EventDispatcherService,
        event_factory=event_factory,
        event_specification=event_specification,
        event_queue=event_queue,
    )

    event_processor_service = providers.Factory(
        domain.event_processor.EventProcessorService,
        event_queue=event_queue,
        event_factory=event_factory,
        event_repository=event_repository,
        subscription_repository=subscription_repository,
        concurrency=config.domain.processor_concurrency.as_int(),
    )
