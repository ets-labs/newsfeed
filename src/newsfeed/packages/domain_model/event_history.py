"""Event history module."""

from typing import Type
from uuid import UUID, uuid4

from newsfeed.packages.infrastructure.event_history_storage import EventHistoryStorage

from .event import EventFQID


class EventHistory:
    """Event history entity."""

    def __init__(self, id: UUID, event_fqid: EventFQID):
        """Initialize entity."""
        assert isinstance(id, UUID)
        self._id = id

        assert isinstance(event_fqid, EventFQID)
        self._event_fqid = event_fqid

    @property
    def id(self):
        """Return id."""
        return self._id

    @property
    def serialized_data(self):
        """Return serialized data."""
        return {
            'id': str(self._id),
            'event_fqid': self._event_fqid.serialized_data,
        }


class EventHistoryFactory:
    """Event history entity factory."""

    def __init__(self, cls: Type[EventHistory]):
        """Initialize factory."""
        assert issubclass(cls, EventHistory)
        self._cls = cls

    def create_new(self, event_fqid: EventFQID) -> EventHistory:
        """Create new entity."""
        return self._cls(
            id=uuid4(),
            event_fqid=event_fqid,
        )

    def create_from_serialized(self, data) -> EventHistory:
        """Create entity from serialized data."""
        return self._cls(
            id=UUID(data['id']),
            event_fqid=EventFQID(
                newsfeed_id=data['event_fqid']['newsfeed_id'],
                event_id=UUID(data['event_fqid']['event_id']),
            ),
        )


class EventHistoryRepository:
    """Event history repository."""

    def __init__(self, factory: EventHistoryFactory, storage: EventHistoryStorage):
        """Initialize repository."""
        assert isinstance(factory, EventHistoryFactory)
        self._factory = factory

        assert isinstance(storage, EventHistoryStorage)
        self._storage = storage

    async def add(self, event_history: EventHistory):
        """Add entity to the repository."""
        await self._storage.add(event_history.serialized_data)
