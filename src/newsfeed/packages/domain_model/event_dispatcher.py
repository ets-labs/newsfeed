"""Event dispatcher module."""

from newsfeed.packages.infrastructure.event_queues import EventQueue

from .event import EventFactory, EventSpecification
from .event_history import EventHistoryFactory


class EventDispatcherService:
    """Event dispatcher service."""

    def __init__(self,
                 factory: EventFactory,
                 specification: EventSpecification,
                 queue: EventQueue,
                 event_history_factory: EventHistoryFactory):
        """Initialize service."""
        assert isinstance(factory, EventFactory)
        self._factory = factory

        assert isinstance(specification, EventSpecification)
        self._specification = specification

        assert isinstance(queue, EventQueue)
        self._queue = queue

        assert isinstance(event_history_factory, EventHistoryFactory)
        self._event_history_factory = event_history_factory

    async def dispatch_event(self, newsfeed_id: str, data: dict):
        """Dispatch event."""
        event = self._factory.create_new(
            newsfeed_id=newsfeed_id,
            data=data,
        )
        self._specification.is_satisfied_by(event)

        _ = self._event_history_factory.create_new()

        await self._queue.put(event.serialized_data)

        return event

