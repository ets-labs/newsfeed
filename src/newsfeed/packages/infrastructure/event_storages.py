"""Infrastructure event storages module."""

import ast
from collections import defaultdict, deque
from operator import itemgetter
from typing import Dict, Deque, Iterable, Union

import aioredis

EventData = Dict[str, Union[str, int]]


class EventStorage:
    """Event storage."""

    def __init__(self, config: Dict[str, str]):
        """Initialize storage."""
        self._config = config

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[EventData]:
        """Return events of specified newsfeed."""
        raise NotImplementedError()

    async def get_by_fqid(self, newsfeed_id: str, event_id: str) -> EventData:
        """Return event of specified newsfeed."""
        raise NotImplementedError()

    async def add(self, event_data: EventData) -> None:
        """Add event to the storage."""
        raise NotImplementedError()

    async def delete_by_fqid(self, newsfeed_id: str, event_id: str) -> None:
        """Delete specified event."""
        raise NotImplementedError()


class InMemoryEventStorage(EventStorage):
    """Event storage that stores events in memory."""

    def __init__(self, config: Dict[str, str]):
        """Initialize queue."""
        super().__init__(config)
        self._storage: Dict[str, Deque[EventData]] = defaultdict(deque)

        self._max_newsfeed_ids = int(config['max_newsfeeds'])
        self._max_events_per_newsfeed_id = int(config['max_events_per_newsfeed'])

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[EventData]:
        """Get events data from storage."""
        newsfeed_storage = self._storage[newsfeed_id]
        return list(newsfeed_storage)

    async def get_by_fqid(self, newsfeed_id: str, event_id: str) -> EventData:
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

    async def add(self, event_data: EventData) -> None:
        """Add event data to the storage."""
        newsfeed_id = str(event_data['newsfeed_id'])

        if len(self._storage) >= self._max_newsfeed_ids:
            raise NewsfeedNumberLimitExceeded(newsfeed_id, self._max_newsfeed_ids)

        newsfeed_storage = self._storage[newsfeed_id]

        if len(newsfeed_storage) >= self._max_events_per_newsfeed_id:
            newsfeed_storage.pop()

        newsfeed_storage.appendleft(event_data)

    async def delete_by_fqid(self, newsfeed_id: str, event_id: str) -> None:
        """Delete data of specified event."""
        newsfeed_storage = self._storage[newsfeed_id]
        event_index = None
        for index, event in enumerate(newsfeed_storage):
            if event['id'] == event_id:
                event_index = index
                break
        if event_index is not None:
            del newsfeed_storage[event_index]


class RedisEventStorage(EventStorage):
    """Event storage that stores events in memory."""

    def __init__(self, config: Dict[str, str]):
        """Initialize queue."""
        super().__init__(config)

        self._max_newsfeed_ids = int(config['max_newsfeeds'])
        self._max_events_per_newsfeed_id = int(config['max_events_per_newsfeed'])

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[EventData]:
        """Get events data from storage."""
        # TODO: Move to factory
        redis = await aioredis.create_redis(
            'redis://redis',
            encoding='utf-8',
        )
        keys = []
        newsfeed_storage = []
        async for key in redis.izscan(f'newsfeed_id:{newsfeed_id}'):
            keys.append(key)

        # TODO:
        #  - Check async
        #  - Write base serializer
        #  - Is it correct place for ordering?
        #  - Ordering by `published_at`?
        for key, _ in keys:
            event = await redis.hgetall(key)
            event['parent_fqid'] = ast.literal_eval(event['parent_fqid'])
            event['child_fqids'] = ast.literal_eval(event['child_fqids'])
            event['first_seen_at'] = ast.literal_eval(event['first_seen_at'])
            event['published_at'] = ast.literal_eval(event['published_at'])
            event['data'] = ast.literal_eval(event['data'])
            newsfeed_storage.append(event)

        # TODO: Move to factory
        redis.close()
        await redis.wait_closed()

        return sorted(
            newsfeed_storage,
            key=itemgetter('published_at'),
            reverse=True,
        )

    async def get_by_fqid(self, newsfeed_id: str, event_id: str) -> EventData:
        """Return data of specified event."""
        # TODO: Move to factory
        redis = await aioredis.create_redis(
            'redis://redis',
            encoding='utf-8',
        )
        event = await redis.hgetall(f'event:{event_id}')

        # TODO: Move to factory
        redis.close()
        await redis.wait_closed()

        if not event:
            raise EventNotFound(
                newsfeed_id=newsfeed_id,
                event_id=event_id,
            )
        else:
            event['parent_fqid'] = ast.literal_eval(event['parent_fqid'])
            event['child_fqids'] = ast.literal_eval(event['child_fqids'])
            event['first_seen_at'] = ast.literal_eval(event['first_seen_at'])
            event['published_at'] = ast.literal_eval(event['published_at'])
            event['data'] = ast.literal_eval(event['data'])
            return event

    async def add(self, event_data: EventData) -> None:
        """Add event data to the storage."""
        newsfeed_id = str(event_data['newsfeed_id'])

        # TODO: Move to factory
        redis = await aioredis.create_redis(
            'redis://redis',
        )

        # TODO: Test the checker
        _, keys = await redis.scan(b'0', match='newsfeed_id:*')
        if len(keys) >= self._max_newsfeed_ids:
            raise NewsfeedNumberLimitExceeded(newsfeed_id,
                                              self._max_newsfeed_ids)
        # TODO: Test the checker
        if redis.zcard(f'newsfeed_id:{newsfeed_id}') \
                >= self._max_events_per_newsfeed_id:
            redis.zpopmin(f'newsfeed_id:{newsfeed_id}')

        await redis.hmset_dict(
            f"event:{event_data['id']}",
            {key: str(value) for key, value in event_data.items()}
        )
        await redis.zadd(
            key=f'newsfeed_id:{newsfeed_id}',
            score=event_data['published_at'],
            member=f"event:{event_data['id']}",
        )

        # TODO: Move to factory
        redis.close()
        await redis.wait_closed()

    async def delete_by_fqid(self, newsfeed_id: str, event_id: str) -> None:
        """Delete data of specified event."""
        # TODO: Move to factory
        redis = await aioredis.create_redis(
            'redis://redis',
            encoding='utf-8',
        )
        event = f'event:{event_id}'
        newsfeed = f'newsfeed_id:{newsfeed_id}'
        await redis.delete(event)
        await redis.zrem(newsfeed, event)

        # TODO: Move to factory
        redis.close()
        await redis.wait_closed()


class EventStorageError(Exception):
    """Event-storage-related error."""

    @property
    def message(self) -> str:
        """Return error message."""
        return 'Newsfeed event storage error'


class NewsfeedNumberLimitExceeded(EventStorageError):
    """Error indicating situations when number of newsfeeds exceeds maximum."""

    def __init__(self, newsfeed_id: str, max_newsfeed_ids: int):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._max_newsfeed_ids = max_newsfeed_ids

    @property
    def message(self) -> str:
        """Return error message."""
        return (
            f'Newsfeed "{self._newsfeed_id}" could not be added to the storage because limit '
            f'of newsfeeds number exceeds maximum {self._max_newsfeed_ids}'
        )


class EventNotFound(EventStorageError):
    """Error indicating situations when event could not be found in the storage."""

    def __init__(self, newsfeed_id: str, event_id: str):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._event_id = event_id

    @property
    def message(self) -> str:
        """Return error message."""
        return f'Event "{self._event_id}" could not be found in newsfeed "{self._newsfeed_id}"'
