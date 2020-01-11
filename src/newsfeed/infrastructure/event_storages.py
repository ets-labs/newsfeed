"""Infrastructure event storages module."""

import json
from contextlib import asynccontextmanager
from collections import defaultdict, deque
from typing import Dict, Deque, Iterable, Union

import aioredis

from .utils import parse_redis_dsn


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
        """Initialize storage."""
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
    """Event storage that stores events in redis."""

    def __init__(self, config: Dict[str, str]):
        """Initialize storage."""
        super().__init__(config)

        redis_config = parse_redis_dsn(config['dsn'])
        self._pool = aioredis.pool.ConnectionsPool(
            address=redis_config['address'],
            db=int(redis_config['db']),
            create_connection_timeout=int(redis_config['connection_timeout']),
            minsize=int(redis_config['minsize']),
            maxsize=int(redis_config['maxsize']),
            encoding='utf-8',
        )

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[EventData]:
        """Get events data from storage."""
        newsfeed_storage = []
        async with self._get_connection() as redis:
            for event in await redis.lrange(key=f'newsfeed_id:{newsfeed_id}',
                                            start=0,
                                            stop=-1):
                newsfeed_storage.append(json.loads(event))
        return newsfeed_storage

    async def get_by_fqid(self, newsfeed_id: str, event_id: str) -> EventData:
        """Return data of specified event."""
        async with self._get_connection() as redis:
            event = await redis.get(f'event:{event_id}')

        if not event:
            raise EventNotFound(
                newsfeed_id=newsfeed_id,
                event_id=event_id,
            )

        return json.loads(event)

    async def add(self, event_data: EventData) -> None:
        """Add event data to the storage."""
        newsfeed_id = str(event_data['newsfeed_id'])

        async with self._get_connection() as redis:
            await redis.lpush(
                key=f'newsfeed_id:{newsfeed_id}',
                value=json.dumps(event_data),
            )
            await redis.append(
                key=f"event:{event_data['id']}",
                value=json.dumps(event_data),
            )

    async def delete_by_fqid(self, newsfeed_id: str, event_id: str) -> None:
        """Delete data of specified event."""
        async with self._get_connection() as redis:
            event_key = f'event:{event_id}'
            newsfeed = f'newsfeed_id:{newsfeed_id}'
            event = await redis.get(event_key)

            if not event:
                raise EventNotFound(
                    newsfeed_id=newsfeed_id,
                    event_id=event_id,
                )

            await redis.lrem(newsfeed, 1, event)
            await redis.delete(event_key)

    @asynccontextmanager
    async def _get_connection(self) -> aioredis.commands.Redis:
        async with self._pool.get() as connection:
            redis = aioredis.commands.Redis(connection)
            yield redis


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
