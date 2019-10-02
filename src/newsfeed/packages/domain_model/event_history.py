"""Event history module."""

from typing import Type
from uuid import UUID, uuid4

from newsfeed.packages.infrastructure.event_history_storage import EventHistoryStorage


class EventHistory:
    """Event history entity."""

    def __init__(self, id: UUID):
        """Initialize entity."""
        assert isinstance(id, UUID)
        self._id = id

    @property
    def id(self):
        """Return id."""
        return self._id

    @property
    def serialized_data(self):
        """Return serialized data."""
        return {
            'id': str(self._id),
        }


class EventHistoryFactory:
    """Event history entity factory."""

    def __init__(self, cls: Type[EventHistory]):
        """Initialize factory."""
        assert issubclass(cls, EventHistory)
        self._cls = cls

    def create_new(self) -> EventHistory:
        """Create new entity."""
        return self._cls(
            id=uuid4(),
        )

    def create_from_serialized(self, data) -> EventHistory:
        """Create entity from serialized data."""
        return self._cls(
            id=UUID(data['id']),
        )


class EventHistoryRepository:
    """Event history repository."""

    def __init__(self, factory: EventHistoryFactory, storage: EventHistoryStorage):
        """Initialize repository."""
        assert isinstance(factory, EventHistoryFactory)
        self._factory = factory

        assert isinstance(storage, EventHistoryStorage)
        self._storage = storage

    async def add(self, history: EventHistory):
        """Add entity to the repository."""
        await self._storage.add(history.serialized_data)
