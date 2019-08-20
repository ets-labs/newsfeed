"""Events module."""

from typing import Type

from newsfeed.packages.infrastructure.event_storage import EventStorage
from newsfeed.packages.infrastructure.event_queues import EventQueue

from .subscriptions import SubscriptionRepository


class Event:
    """Event entity."""


class EventFactory:
    """Event entity factory."""

    def __init__(self, cls: Type[Event]):
        """Initialize factory."""
        assert issubclass(cls, Event)
        self._cls = cls


class EventSpecification:
    """Event specification."""

    def __init__(self):
        """Initialize specification."""


class EventRepository:
    """Event repository."""

    def __init__(self, factory: EventFactory, storage: EventStorage):
        """Initialize repository."""
        assert isinstance(factory, EventFactory)
        self._factory = factory

        assert isinstance(storage, EventStorage)
        self._storage = storage


class EventDispatcherService:
    """Event dispatcher service."""

    def __init__(self,
                 factory: EventFactory,
                 specification: EventSpecification,
                 queue: EventQueue):
        """Initialize service."""
        assert isinstance(factory, EventFactory)
        self._factory = factory

        assert isinstance(specification, EventSpecification)
        self._specification = specification

        assert isinstance(queue, EventQueue)
        self._queue = queue


class EventPublisherService:
    """Event publisher service."""

    def __init__(self,
                 queue: EventQueue,
                 event_repository: EventRepository,
                 subscription_repository: SubscriptionRepository):
        """Initialize service."""
        assert isinstance(queue, EventQueue)
        self._queue = queue

        assert isinstance(event_repository, EventRepository)
        self._event_repository = event_repository

        assert isinstance(subscription_repository, SubscriptionRepository)
        self._subscription_repository = subscription_repository
