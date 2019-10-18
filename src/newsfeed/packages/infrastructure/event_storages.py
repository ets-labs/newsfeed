"""Infrastructure event storages module."""

from collections import defaultdict, deque


class EventStorage:
    """Event storage."""

    def __init__(self, config):
        """Initialize storage."""
        self._config = config

    async def get_by_newsfeed_id(self, newsfeed_id):
        """Return events of specified newsfeed."""
        raise NotImplementedError()

    async def get_by_fqid(self, newsfeed_id, event_id):
        """Return event of specified newsfeed."""
        raise NotImplementedError()

    async def add(self, event_data):
        """Add event to the storage."""
        raise NotImplementedError()

    async def delete_by_fqid(self, newsfeed_id, event_id):
        """Delete specified event."""
        raise NotImplementedError()


class InMemoryEventStorage(EventStorage):
    """Event storage that stores events in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._storage = defaultdict(deque)

        self._max_newsfeed_ids = int(config['max_newsfeeds'])
        self._max_events_per_newsfeed_id = int(config['max_events_per_newsfeed'])

    async def get_by_newsfeed_id(self, newsfeed_id):
        """Get events data from storage."""
        newsfeed_storage = self._storage[newsfeed_id]
        return list(newsfeed_storage)

    async def get_by_fqid(self, newsfeed_id, event_id):
        """Return data of specified event."""
        newsfeed_storage = self._storage[newsfeed_id]
        for event in newsfeed_storage:
            if event['id'] == event_id:
                return event
        else:
            raise EventNotFound(
                newsfeed_id=newsfeed_id,
                event_id=event_id,
            )

    async def add(self, event_data):
        """Add event data to the storage."""
        newsfeed_id = event_data['newsfeed_id']

        if len(self._storage) >= self._max_newsfeed_ids:
            raise NewsfeedNumberLimitExceeded(newsfeed_id, self._max_newsfeed_ids)

        newsfeed_storage = self._storage[newsfeed_id]

        if len(newsfeed_storage) >= self._max_events_per_newsfeed_id:
            newsfeed_storage.pop()

        newsfeed_storage.appendleft(event_data)

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


class EventStorageError(Exception):
    """Event-storage-related error."""

    @property
    def message(self):
        """Return error message."""
        return 'Newsfeed event storage error'


class NewsfeedNumberLimitExceeded(EventStorageError):
    """Error indicating situations when number of newsfeeds exceeds maximum."""

    def __init__(self, newsfeed_id, max_newsfeed_ids):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._max_newsfeed_ids = max_newsfeed_ids

    @property
    def message(self):
        """Return error message."""
        return (
            f'Newsfeed "{self._newsfeed_id}" could not be added to the storage because limit '
            f'of newsfeeds number exceeds maximum {self._max_newsfeed_ids}'
        )


class EventNotFound(EventStorageError):
    """Error indicating situations when event could not be found in the storage."""

    def __init__(self, newsfeed_id, event_id):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._event_id = event_id

    @property
    def message(self):
        """Return error message."""
        return f'Event "{self._event_id}" could not be found in newsfeed "{self._newsfeed_id}"'
