"""Containers module."""

from aiohttp import web
from dependency_injector import containers, providers
from dependency_injector.ext import aiohttp

from newsfeed import core, infrastructure, domainmodel, webapi


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
        domainmodel.newsfeed_id.NewsfeedIDSpecification,
        max_length=config.domainmodel.newsfeed_id_length,
    )

    # Domain model -> Subscriptions

    subscription_factory = providers.Factory(domainmodel.subscription.SubscriptionFactory)

    subscription_specification = providers.Singleton(
        domainmodel.subscription.SubscriptionSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    subscription_repository = providers.Singleton(
        domainmodel.subscription.SubscriptionRepository,
        factory=subscription_factory,
        storage=subscription_storage,
    )

    subscription_service = providers.Singleton(
        domainmodel.subscription.SubscriptionService,
        factory=subscription_factory,
        specification=subscription_specification,
        repository=subscription_repository,
    )

    # Domain model -> Events

    event_factory = providers.Factory(domainmodel.event.EventFactory)

    event_specification = providers.Singleton(
        domainmodel.event.EventSpecification,
        newsfeed_id_specification=newsfeed_id_specification,
    )

    event_repository = providers.Singleton(
        domainmodel.event.EventRepository,
        factory=event_factory,
        storage=event_storage,
    )

    # Domain model -> Services

    event_dispatcher_service = providers.Factory(
        domainmodel.event_dispatcher.EventDispatcherService,
        event_factory=event_factory,
        event_specification=event_specification,
        event_queue=event_queue,
    )

    event_processor_service = providers.Factory(
        domainmodel.event_processor.EventProcessorService,
        event_queue=event_queue,
        event_factory=event_factory,
        event_repository=event_repository,
        subscription_repository=subscription_repository,
        concurrency=config.domainmodel.processor_concurrency.as_int(),
    )

    # Web API

    web_app = aiohttp.Application(web.Application)

    run_web_app = providers.Callable(
        web.run_app,
        port=config.webapi.port.as_int(),
        print=None,
    )

    # Web API -> Subscriptions

    get_subscriptions_view = aiohttp.View(
        webapi.handlers.subscriptions.get_subscriptions_handler,
        subscription_service=subscription_service,
    )

    add_subscription_view = aiohttp.View(
        webapi.handlers.subscriptions.post_subscription_handler,
        subscription_service=subscription_service,
    )

    delete_subscription_view = aiohttp.View(
        webapi.handlers.subscriptions.delete_subscription_handler,
        subscription_service=subscription_service,
    )

    get_subscribers_view = aiohttp.View(
        webapi.handlers.subscriptions.get_subscriber_subscriptions_handler,
        subscription_service=subscription_service,
    )

    # Web API -> Events

    get_events_view = aiohttp.View(
        webapi.handlers.events.get_events_handler,
        event_repository=event_repository,
    )

    add_event_view = aiohttp.View(
        webapi.handlers.events.post_event_handler,
        event_dispatcher_service=event_dispatcher_service,
    )

    delete_event_view = aiohttp.View(
        webapi.handlers.events.delete_event_handler,
        event_dispatcher_service=event_dispatcher_service,
    )

    # Web API -> Miscellaneous

    get_status_view = aiohttp.View(webapi.handlers.misc.get_status_handler)

    get_docs_handler = aiohttp.View(
        webapi.handlers.misc.get_openapi_schema_handler,
        base_path=config.base_path,
    )
