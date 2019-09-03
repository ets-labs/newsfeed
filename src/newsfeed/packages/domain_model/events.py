"""Events module."""

from typing import Type, Mapping
from uuid import UUID, uuid4
from datetime import datetime

from newsfeed.packages.infrastructure.event_storage import EventStorage
from newsfeed.packages.infrastructure.event_queues import EventQueue

from .subscriptions import SubscriptionRepository


class Event:
    """Event entity."""

    def __init__(self, id: UUID, newsfeed_id: str, data: Mapping, first_seen_at: datetime,
                 published_at: datetime):
        """Initialize entity."""
        assert isinstance(id, UUID)
        self._id = id

        assert isinstance(newsfeed_id, str)
        self._newsfeed_id = newsfeed_id

        assert isinstance(data, Mapping)
        self._data = data

        assert isinstance(first_seen_at, datetime)
        self._first_seen_at = first_seen_at

        if published_at is not None:
            assert isinstance(published_at, datetime)
        self._published_at = published_at

    @property
    def id(self):
        """Return id."""
        return self._id

    @property
    def serialized_data(self):
        """Return serialized data."""
        return {
            'id': str(self._id),
            'newsfeed_id': self._newsfeed_id,
            'data': self._data,
            'first_seen_at': self._first_seen_at.timestamp(),
            'published_at': self._published_at.timestamp() if self._published_at else None,
        }


class EventFactory:
    """Event entity factory."""

    def __init__(self, cls: Type[Event]):
        """Initialize factory."""
        assert issubclass(cls, Event)
        self._cls = cls

    def create_new(self, newsfeed_id, data) -> Event:
        """Create new event."""
        return self._cls(
            id=uuid4(),
            newsfeed_id=newsfeed_id,
            data=data,
            first_seen_at=datetime.utcnow(),
            published_at=None,
        )

    def create_from_serialized(self, data) -> Event:
        """Create new event from serialized data."""
        return self._cls(
            id=UUID(data['id']),
            newsfeed_id=data['newsfeed_id'],
            data=data['data'],
            first_seen_at=datetime.utcfromtimestamp(data['first_seen_at']),
            published_at=(
                datetime.utcfromtimestamp(data['published_at']) if data['published_at'] else None
            ),
        )


class EventSpecification:
    """Event specification."""

    def __init__(self):
        """Initialize specification."""

    def is_satisfied_by(self, event: Event):
        """Check if event satisfies specification."""
        return True


class EventRepository:
    """Event repository."""

    def __init__(self, factory: EventFactory, storage: EventStorage):
        """Initialize repository."""
        assert isinstance(factory, EventFactory)
        self._factory = factory

        assert isinstance(storage, EventStorage)
        self._storage = storage

    async def add(self, event: Event):
        """Add event to repository."""
        await self._storage.add(event.serialized_data)

    async def get_newsfeed(self, newsfeed_id):
        """Return newsfeed events."""
        return await self._storage.get_newsfeed(newsfeed_id)


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

    async def dispatch_event(self, event_data: dict):
        """Dispatch event."""
        event = self._factory.create_new(**event_data)
        self._specification.is_satisfied_by(event)
        await self._queue.put(event.serialized_data)
        return event


class EventPublisherService:
    """Event publisher service."""

    def __init__(self,
                 event_queue: EventQueue,
                 event_factory: EventFactory,
                 event_repository: EventRepository,
                 subscription_repository: SubscriptionRepository):
        """Initialize service."""
        assert isinstance(event_queue, EventQueue)
        self._event_queue = event_queue

        assert isinstance(event_factory, EventFactory)
        self._event_factory = event_factory

        assert isinstance(event_repository, EventRepository)
        self._event_repository = event_repository

        assert isinstance(subscription_repository, SubscriptionRepository)
        self._subscription_repository = subscription_repository

    async def process_event(self):
        """Process event."""
        event_data = await self._event_queue.get()
        event = self._event_factory.create_from_serialized(event_data)
        await self._event_repository.add(event)
