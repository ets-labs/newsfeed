"""Event dispatcher module."""

from newsfeed.packages.infrastructure.event_queues import EventQueue

from .event import EventFactory, EventSpecification


class EventDispatcherService:
    """Event dispatcher service."""

    def __init__(self,
                 event_factory: EventFactory,
                 event_specification: EventSpecification,
                 event_queue: EventQueue):
        """Initialize service."""
        assert isinstance(event_factory, EventFactory)
        self._event_factory = event_factory

        assert isinstance(event_specification, EventSpecification)
        self._event_specification = event_specification

        assert isinstance(event_queue, EventQueue)
        self._event_queue = event_queue

    async def dispatch_event(self, newsfeed_id: str, data: dict):
        """Dispatch event."""
        event = self._event_factory.create_new(
            newsfeed_id=newsfeed_id,
            data=data,
        )
        self._event_specification.is_satisfied_by(event)
        await self._event_queue.put(event.serialized_data)
        return event

