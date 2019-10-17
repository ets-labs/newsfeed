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

    async def put(self, event_data):
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
        self._queue = asyncio.Queue()

    async def get(self):
        """Get event data from queue."""
        return await self._queue.get()

    async def put(self, event_data):
        """Put event data to queue."""
        try:
            self._queue.put_nowait(event_data)
        except asyncio.QueueFull:
            raise QueueFull('Event queue is full')

    async def is_empty(self):
        """Check if queue is empty."""
        return self._queue.empty()


class QueueFull(Exception):
    """Error indicating situations when queue can not accept messages due to being full."""
