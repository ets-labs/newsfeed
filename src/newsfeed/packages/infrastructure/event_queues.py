"""Infrastructure event queues module."""

import asyncio
from typing import Dict, Tuple, Union


Action = str
EventData = Dict[str, Union[str, int]]
Message = Tuple[Action, EventData]


class EventQueue:
    """Event queue."""

    def __init__(self, config: Dict[str, str]):
        """Initialize queue."""
        self._config = config

    async def get(self) -> Message:
        """Get message from queue."""
        raise NotImplementedError()

    async def put(self, message: Message) -> None:
        """Put message to queue."""
        raise NotImplementedError()

    async def is_empty(self) -> bool:
        """Check if queue is empty."""
        raise NotImplementedError()


class InMemoryEventQueue(EventQueue):
    """Event queue that stores messages in memory."""

    def __init__(self, config: Dict[str, str]):
        """Initialize queue."""
        super().__init__(config)
        self._queue: asyncio.Queue[Message] = asyncio.Queue()

    async def get(self) -> Message:
        """Get message from queue."""
        return await self._queue.get()

    async def put(self, message: Message) -> None:
        """Put message to queue."""
        try:
            self._queue.put_nowait(message)
        except asyncio.QueueFull:
            raise QueueFull(self._queue.maxsize)

    async def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()


class EventQueueError(Exception):
    """Event-queue-related error."""

    @property
    def message(self):
        """Return error message."""
        return 'Newsfeed event queue error'


class QueueFull(EventQueueError):
    """Error indicating situations when queue can not accept messages due to being full."""

    def __init__(self, queue_size):
        """Initialize error."""
        self._queue_size = queue_size

    @property
    def message(self):
        """Return error message."""
        return (
            f'Newsfeed event queue can not accept message because queue size limit exceeds '
            f'maximum {self._queue_size}'
        )
