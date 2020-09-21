"""Event processor module."""

import asyncio
import dataclasses
from uuid import UUID
from typing import List, Dict, Any

from newsfeed.infrastructure.event_queues import EventQueue

from .event import EventFactory, EventRepository, EventFQID
from .subscription import SubscriptionRepository


@dataclasses.dataclass
class EventProcessorService:

    event_queue: EventQueue
    event_factory: EventFactory
    event_repository: EventRepository
    subscription_repository: SubscriptionRepository
    concurrency: int

    _tasks: List['asyncio.Task[None]'] = dataclasses.field(default_factory=list)

    def start_processing(self) -> None:
        loop = asyncio.get_event_loop()

        self._tasks = [
            loop.create_task(self._processor_loop())
            for _ in range(int(self.concurrency))
        ]

    def stop_processing(self) -> None:
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def process_event(self) -> None:
        """Process event."""
        action, data = await self.event_queue.get()

        if action == 'post':
            await self.process_new_event(data)
        elif action == 'delete':
            await self.process_event_deletion(data)
        else:
            ...

    async def process_new_event(self, data: Dict[str, Any]) -> None:
        """Process posting of new event."""
        event = self.event_factory.create_from_serialized(data)
        subscriptions = await self.subscription_repository.get_by_to_newsfeed_id(
            newsfeed_id=event.newsfeed_id,
        )

        subscriber_events = [
            self.event_factory.create_new(
                newsfeed_id=subscription.newsfeed_id,
                data=event.data,
                parent_fqid=event.fqid,
            )
            for subscription in subscriptions
        ]
        event.track_child_fqids(
            [
                subscriber_event.fqid
                for subscriber_event in subscriber_events
            ]
        )

        for event in [event] + subscriber_events:
            event.track_publishing_time()
            await self.event_repository.add(event)

    async def process_event_deletion(self, data: Dict[str, Any]) -> None:
        """Process deletion of an existing event."""
        event = await self.event_repository.get_by_fqid(
            EventFQID(
                newsfeed_id=str(data['newsfeed_id']),
                event_id=UUID(data['event_id']),
            ),
        )

        for child_event_fqid in event.child_fqids:
            await self.event_repository.delete_by_fqid(child_event_fqid)

        await self.event_repository.delete_by_fqid(event.fqid)

    async def _processor_loop(self) -> None:
        while True:
            await self.process_event()
