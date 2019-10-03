"""Events module."""

import asyncio

from newsfeed.packages.infrastructure.event_queues import EventQueue

from .event import EventFactory, EventRepository
from .event_history import EventHistoryFactory, EventHistoryRepository
from .subscription import SubscriptionRepository


class EventPublisherService:
    """Event publisher service."""

    def __init__(self,
                 event_queue: EventQueue,
                 event_factory: EventFactory,
                 event_repository: EventRepository,
                 event_history_factory: EventHistoryFactory,
                 event_history_repository: EventHistoryRepository,
                 subscription_repository: SubscriptionRepository):
        """Initialize service."""
        assert isinstance(event_queue, EventQueue)
        self._event_queue = event_queue

        assert isinstance(event_factory, EventFactory)
        self._event_factory = event_factory

        assert isinstance(event_repository, EventRepository)
        self._event_repository = event_repository

        assert isinstance(event_history_factory, EventHistoryFactory)
        self._event_history_factory = event_history_factory

        assert isinstance(event_history_repository, EventHistoryRepository)
        self._event_history_repository = event_history_repository

        assert isinstance(subscription_repository, SubscriptionRepository)
        self._subscription_repository = subscription_repository

    async def process_event(self):
        """Process event."""
        event_data, event_history_data = await self._event_queue.get()

        event = self._event_factory.create_from_serialized(event_data)
        event_history = self._event_history_factory.create_from_serialized(event_history_data)

        subscriptions = await self._subscription_repository.get_subscriptions_to(event.newsfeed_id)

        events_for_publishing = [event]
        events_for_publishing += [
            self._event_factory.create_new(
                newsfeed_id=subscription.from_newsfeed_id,
                data=event.data,
                parent_id=event.id,
            )
            for subscription in subscriptions
        ]

        for event in events_for_publishing:
            event.track_publishing_time()

        await asyncio.gather(
            self._event_repository.add_batch(events_for_publishing),
            self._event_history_repository.add(event_history),
        )
