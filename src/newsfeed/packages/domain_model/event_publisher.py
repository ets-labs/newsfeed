"""Events module."""

import asyncio

from newsfeed.packages.infrastructure.event_queues import EventQueue

from .event import EventFactory, EventRepository
from .subscription import SubscriptionRepository


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
        subscriptions = await self._subscription_repository.get_subscriptions_to(event.newsfeed_id)

        subscriber_events = [
            self._event_factory.create_new(
                newsfeed_id=subscription.from_newsfeed_id,
                data=event.data,
                parent_id=event.fqid,
            )
            for subscription in subscriptions
        ]
        event.track_child_event_fqids(
            [
                subscriber_event.fqid
                for subscriber_event in subscriber_events
            ]
        )

        events_for_publishing = [event]
        events_for_publishing += subscriber_events

        for event in events_for_publishing:
            event.track_publishing_time()
            await self._event_repository.add(event)
