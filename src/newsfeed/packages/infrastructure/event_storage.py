"""Infrastructure event storage module."""

from collections import defaultdict, deque


class EventStorage:
    """Event storage."""

    def __init__(self, config):
        """Initialize storage."""
        self._config = config

    async def add(self, event_data):
        """Add event data to the storage."""
        raise NotImplementedError()

    async def get_newsfeed(self, newsfeed_id):
        """Get events data from storage."""
        raise NotImplementedError()


class AsyncInMemoryEventStorage(EventStorage):
    """Async event storage that stores events in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._storage = defaultdict(deque)

    async def add(self, event_data):
        """Add event data to the storage."""
        newsfeed_id = event_data['newsfeed_id']
        newsfeed_storage = self._storage[newsfeed_id]
        newsfeed_storage.appendleft(event_data)

    async def get_newsfeed(self, newsfeed_id):
        """Get events data from storage."""
        newsfeed_storage = self._storage[newsfeed_id]
        return list(newsfeed_storage)
