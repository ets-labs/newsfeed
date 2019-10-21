"""Infrastructure event queues module."""

import asyncio


class EventQueue:
    """Event queue."""

    def __init__(self, config):
        """Initialize queue."""
        self._config = config

    async def get(self):
        """Get event data from queue."""
        raise NotImplementedError()

    async def put(self, data):
        """Put event data to queue."""
        raise NotImplementedError()

    async def is_empty(self):
        """Check if queue is empty."""
        raise NotImplementedError()


class InMemoryEventQueue(EventQueue):
    """Event queue that stores events in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._queue = asyncio.Queue(maxsize=int(config['max_size']))

    async def get(self):
        """Get event data from queue."""
        return await self._queue.get()

    async def put(self, data):
        """Put event data to queue."""
        try:
            self._queue.put_nowait(data)
        except asyncio.QueueFull:
            raise QueueFull(self._queue.maxsize)

    async def is_empty(self):
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
