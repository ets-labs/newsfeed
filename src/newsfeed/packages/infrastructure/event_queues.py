"""Infrastructure event queues module."""

import asyncio


class EventQueue:
    """Event queue."""

    def __init__(self, config):
        """Initialize queue."""
        self._config = config

    async def put(self, event_data):
        """Put event data to queue."""
        raise NotImplementedError()


class AsyncInMemoryEventQueue(EventQueue):
    """Async event queue that stores events in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._queue = asyncio.Queue()

    async def put(self, event_data):
        """Put event data to queue."""
        self._queue.put_nowait(event_data)

    async def get(self):
        """Get event data from queue."""
        return await self._queue.get()
