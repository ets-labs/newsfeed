"""Events module."""

from __future__ import annotations

from typing import Dict, List, Tuple, Sequence, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from newsfeed.infrastructure.event_storages import EventStorage
from .newsfeed_id import NewsfeedIDSpecification


class EventFQID:
    """Event fully-qualified identifier."""

    def __init__(self, newsfeed_id: str, event_id: UUID):
        """Initialize object."""
        assert isinstance(newsfeed_id, str)
        self.newsfeed_id = newsfeed_id

        assert isinstance(event_id, UUID)
        self.event_id = event_id

    @classmethod
    def from_serialized_data(cls, data: Tuple[str, str]) -> EventFQID:
        """Create instance from serialized data."""
        return cls(data[0], UUID(data[1]))

    @property
    def serialized_data(self) -> Tuple[str, str]:
        """Return serialized data."""
        return self.newsfeed_id, str(self.event_id)


class Event:
    """Event entity."""

    def __init__(self,
                 id: UUID,
                 newsfeed_id: str,
                 data: Dict[Any, Any],
                 parent_fqid: Optional[EventFQID],
                 child_fqids: Sequence[EventFQID],
                 first_seen_at: datetime,
                 published_at: Optional[datetime]):
        """Initialize entity."""
        assert isinstance(id, UUID)
        self._id = id

        assert isinstance(newsfeed_id, str)
        self._newsfeed_id = newsfeed_id

        assert isinstance(data, Dict)
        self._data = data

        if parent_fqid is not None:
            assert isinstance(parent_fqid, EventFQID)
        self._parent_fqid = parent_fqid

        assert isinstance(child_fqids, Sequence)
        for child_fqid in child_fqids:
            assert isinstance(child_fqid, EventFQID)
        self._child_fqids = list(child_fqids)

        assert isinstance(first_seen_at, datetime)
        self._first_seen_at = first_seen_at

        if published_at is not None:
            assert isinstance(published_at, datetime)
        self._published_at = published_at

    @property
    def id(self) -> UUID:
        """Return id."""
        return self._id

    @property
    def newsfeed_id(self) -> str:
        """Return newsfeed id."""
        return self._newsfeed_id

    @property
    def fqid(self) -> EventFQID:
        """Return FQID (Fully-Qualified ID)."""
        return EventFQID(self.newsfeed_id, self.id)

    @property
    def parent_fqid(self) -> Optional[EventFQID]:
        """Return parent FQID."""
        return self._parent_fqid

    @property
    def child_fqids(self) -> Sequence[EventFQID]:
        """Return list of child FQIDs."""
        return list(self._child_fqids)

    @property
    def data(self) -> Dict[Any, Any]:
        """Return data."""
        return dict(self._data)

    @property
    def first_seen_at(self) -> datetime:
        """Return first seen time."""
        return self._first_seen_at

    @property
    def published_at(self) -> Optional[datetime]:
        """Return publishing time."""
        return self._published_at

    def track_publishing_time(self) -> None:
        """Track publishing time."""
        self._published_at = datetime.utcnow()

    def track_child_fqids(self, child_fqids: Sequence[EventFQID]) -> None:
        """Track child FQIDs.

        This method accumulates child FQIDs.
        """
        assert isinstance(child_fqids, Sequence)
        for child_fqid in child_fqids:
            assert isinstance(child_fqid, EventFQID)
        self._child_fqids.extend(child_fqids)

    @property
    def serialized_data(self) -> Dict[str, Any]:
        """Return serialized data."""
        return {
            'id': str(self._id),
            'newsfeed_id': self._newsfeed_id,
            'data': self._data,
            'parent_fqid': self._parent_fqid.serialized_data if self._parent_fqid else None,
            'child_fqids': [
                child_fqid.serialized_data
                for child_fqid in self._child_fqids
            ],
            'first_seen_at': self._first_seen_at.timestamp(),
            'published_at': self._published_at.timestamp() if self._published_at else None,
        }

    @classmethod
    def create_from_serialized(cls, data: Dict[str, Any]) -> Event:
        """Create instance from serialized data."""
        return cls(
            id=UUID(data['id']),
            newsfeed_id=data['newsfeed_id'],
            data=data['data'],
            parent_fqid=(
                EventFQID.from_serialized_data(data['parent_fqid'])
                if data['parent_fqid']
                else None
            ),
            child_fqids=[
                EventFQID.from_serialized_data(child_fqid)
                for child_fqid in data['child_fqids'] or []
            ],
            first_seen_at=datetime.utcfromtimestamp(data['first_seen_at']),
            published_at=(
                datetime.utcfromtimestamp(data['published_at']) if data['published_at'] else None
            ),
        )


class EventFactory:
    """Event entity factory."""

    cls = Event

    def create_new(self,
                   newsfeed_id: str,
                   data: Dict[Any, Any],
                   parent_fqid: Optional[EventFQID] = None) -> Event:
        """Create new instance."""
        return self.cls(
            id=uuid4(),
            newsfeed_id=newsfeed_id,
            data=data,
            parent_fqid=parent_fqid,
            child_fqids=[],
            first_seen_at=datetime.utcnow(),
            published_at=None,
        )

    def create_from_serialized(self, data: Dict[str, Any]) -> Event:
        """Create instance from serialized data."""
        return self.cls.create_from_serialized(data)


class EventSpecification:
    """Event specification."""

    def __init__(self, newsfeed_id_specification: NewsfeedIDSpecification):
        """Initialize specification."""
        self._newsfeed_id_specification = newsfeed_id_specification

    def is_satisfied_by(self, event: Event) -> bool:
        """Check if event satisfies specification."""
        self._newsfeed_id_specification.is_satisfied_by(event.newsfeed_id)
        return True


class EventRepository:
    """Event repository."""

    def __init__(self, factory: EventFactory, storage: EventStorage):
        """Initialize repository."""
        assert isinstance(factory, EventFactory)
        self._factory = factory

        assert isinstance(storage, EventStorage)
        self._storage = storage

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> List[Event]:
        """Return events of specified newsfeed."""
        newsfeed_events_data = await self._storage.get_by_newsfeed_id(newsfeed_id)
        return [
            self._factory.create_from_serialized(event_data)
            for event_data in newsfeed_events_data
        ]

    async def get_by_fqid(self, fqid: EventFQID) -> Event:
        """Return event by its FQID."""
        event_data = await self._storage.get_by_fqid(
            newsfeed_id=fqid.newsfeed_id,
            event_id=str(fqid.event_id),
        )
        return self._factory.create_from_serialized(event_data)

    async def add(self, event: Event) -> None:
        """Add event to repository."""
        await self._storage.add(event.serialized_data)

    async def delete_by_fqid(self, fqid: EventFQID) -> None:
        """Delete event by its FQID."""
        await self._storage.delete_by_fqid(
            newsfeed_id=fqid.newsfeed_id,
            event_id=str(fqid.event_id),
        )
