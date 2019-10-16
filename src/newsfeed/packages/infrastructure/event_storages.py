"""Infrastructure event storages module."""

from collections import defaultdict, deque


class EventStorage:
    """Event storage."""

    def __init__(self, config):
        """Initialize storage."""
        self._config = config

    async def add(self, event_data):
        """Add event data to the storage."""
        raise NotImplementedError()

    async def get_by_fqid(self, newsfeed_id, event_id):
        """Return data of specified event."""

    async def delete_by_fqid(self, newsfeed_id, event_id):
        """Delete data of specified event."""

    async def get_newsfeed(self, newsfeed_id):
        """Get events data from storage."""
        raise NotImplementedError()


class InMemoryEventStorage(EventStorage):
    """Event storage that stores events in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._storage = defaultdict(deque)

    async def add(self, event_data):
        """Add event data to the storage."""
        newsfeed_id = event_data['newsfeed_id']
        newsfeed_storage = self._storage[newsfeed_id]
        newsfeed_storage.appendleft(event_data)

    async def get_by_fqid(self, newsfeed_id, event_id):
        """Return data of specified event."""
        newsfeed_storage = self._storage[newsfeed_id]
        for event in newsfeed_storage:
            if event['id'] == event_id:
                return event
        else:
            raise RuntimeError(
                f'Event "{event_id}" could not be found in newsfeed "{newsfeed_id}"',
            )

    async def delete_by_fqid(self, newsfeed_id, event_id):
        """Delete data of specified event."""
        newsfeed_storage = self._storage[newsfeed_id]
        event_index = None
        for index, event in enumerate(newsfeed_storage):
            if event['id'] == event_id:
                event_index = index
                break
        if event_index is not None:
            del newsfeed_storage[event_index]

    async def get_newsfeed(self, newsfeed_id):
        """Get events data from storage."""
        newsfeed_storage = self._storage[newsfeed_id]
        return list(newsfeed_storage)
