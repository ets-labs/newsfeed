"""Containers module."""

import logging.config

from dependency_injector import containers, providers

from .loop import configure_event_loop
from .infrastructure import event_queues, event_storages, subscription_storages
from .domain import newsfeed_id, event, subscription, event_processor, event_dispatcher


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    configure_logging = providers.Callable(
        logging.config.dictConfig,
        config=config.logging,
    )

    configure_event_loop = providers.Callable(
        configure_event_loop,
        enable_uvloop=config.enable_uvloop,
    )

    # Infrastructure

    event_queue = providers.Singleton(
        event_queues.InMemoryEventQueue,
        config=config.infrastructure.event_queue,
    )

    event_storage = providers.Singleton(
        event_storages.InMemoryEventStorage,
        config=config.infrastructure.event_storage,
    )

    subscription_storage = providers.Singleton(
        subscription_storages.InMemorySubscriptionStorage,
        config=config.infrastructure.subscription_storage,
    )

    # Domain

    newsfeed_id_specification = providers.Singleton(
        newsfeed_id.NewsfeedIDSpecification,
        max_length=config.domain.newsfeed_id_length,
    )

    # Domain -> Subscriptions

    subscription_factory = providers.Factory(subscription.SubscriptionFactory)

    subscription_specification = providers.Singleton(
        subscription.SubscriptionSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    subscription_repository = providers.Singleton(
        subscription.SubscriptionRepository,
        factory=subscription_factory,
        storage=subscription_storage,
    )

    subscription_service = providers.Singleton(
        subscription.SubscriptionService,
        factory=subscription_factory,
        specification=subscription_specification,
        repository=subscription_repository,
    )

    # Domain -> Events

    event_factory = providers.Factory(event.EventFactory)

    event_specification = providers.Singleton(
        event.EventSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    event_repository = providers.Singleton(
        event.EventRepository,
        factory=event_factory,
        storage=event_storage,
    )

    # Domain -> Services

    event_dispatcher_service = providers.Factory(
        event_dispatcher.EventDispatcherService,
        event_factory=event_factory,
        event_specification=event_specification,
        event_queue=event_queue,
    )

    event_processor_service = providers.Factory(
        event_processor.EventProcessorService,
        event_queue=event_queue,
        event_factory=event_factory,
        event_repository=event_repository,
        subscription_repository=subscription_repository,
        concurrency=config.domain.processor_concurrency.as_int(),
    )
