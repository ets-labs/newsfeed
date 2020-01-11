"""Infrastructure subscription storages module."""

import json
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Iterable, Deque, Dict, Union

import aioredis

from .utils import parse_redis_dsn


SubscriptionData = Dict[str, Union[str, int]]


class SubscriptionStorage:
    """Subscription storage."""

    def __init__(self, config: Dict[str, str]):
        """Initialize storage."""
        self._config = config

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[SubscriptionData]:
        """Return subscriptions of specified newsfeed."""
        raise NotImplementedError()

    async def get_by_to_newsfeed_id(self, newsfeed_id: str) -> Iterable[SubscriptionData]:
        """Return subscriptions to specified newsfeed."""
        raise NotImplementedError()

    async def get_by_fqid(self, newsfeed_id: str, subscription_id: str) -> SubscriptionData:
        """Return subscription of specified newsfeed."""
        raise NotImplementedError()

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str) -> SubscriptionData:
        """Return subscription between specified newsfeeds."""
        raise NotImplementedError()

    async def add(self, subscription_data: SubscriptionData) -> None:
        """Add subscription data to the storage."""
        raise NotImplementedError()

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str) -> None:
        """Delete specified subscription."""
        raise NotImplementedError()


class InMemorySubscriptionStorage(SubscriptionStorage):
    """Subscription storage that stores subscriptions in memory."""

    def __init__(self, config: Dict[str, str]):
        """Initialize queue."""
        super().__init__(config)
        self._subscriptions_storage: Dict[str, Deque[SubscriptionData]] = defaultdict(deque)
        self._subscribers_storage: Dict[str, Deque[SubscriptionData]] = defaultdict(deque)

        self._max_newsfeed_ids = int(config['max_newsfeeds'])
        self._max_subscriptions_per_newsfeed = int(config['max_subscriptions_per_newsfeed'])

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[SubscriptionData]:
        """Return subscriptions of specified newsfeed."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        return list(newsfeed_subscriptions_storage)

    async def get_by_to_newsfeed_id(self, newsfeed_id: str) -> Iterable[SubscriptionData]:
        """Return subscriptions to specified newsfeed."""
        newsfeed_subscribers_storage = self._subscribers_storage[newsfeed_id]
        return list(newsfeed_subscribers_storage)

    async def get_by_fqid(self, newsfeed_id: str, subscription_id: str) -> SubscriptionData:
        """Return subscription of specified newsfeed."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        for subscription_data in newsfeed_subscriptions_storage:
            if subscription_data['id'] == subscription_id:
                return subscription_data
        else:
            raise SubscriptionNotFound(
                newsfeed_id=newsfeed_id,
                subscription_id=subscription_id,
            )

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str) -> SubscriptionData:
        """Return subscription between specified newsfeeds."""
        if newsfeed_id not in self._subscriptions_storage:
            raise SubscriptionBetweenNotFound(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        for subscription_data in newsfeed_subscriptions_storage:
            if subscription_data['to_newsfeed_id'] == to_newsfeed_id:
                return subscription_data
        else:
            raise SubscriptionBetweenNotFound(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )

    async def add(self, subscription_data: SubscriptionData) -> None:
        """Add subscription data to the storage."""
        subscription_id = str(subscription_data['id'])
        newsfeed_id = str(subscription_data['newsfeed_id'])
        to_newsfeed_id = str(subscription_data['to_newsfeed_id'])

        if len(self._subscriptions_storage) >= self._max_newsfeed_ids:
            raise NewsfeedNumberLimitExceeded(newsfeed_id, self._max_newsfeed_ids)

        subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        subscribers_storage = self._subscribers_storage[to_newsfeed_id]

        if len(subscriptions_storage) >= self._max_subscriptions_per_newsfeed:
            raise SubscriptionNumberLimitExceeded(
                subscription_id,
                newsfeed_id,
                to_newsfeed_id,
                self._max_subscriptions_per_newsfeed,
            )

        subscriptions_storage.appendleft(subscription_data)
        subscribers_storage.appendleft(subscription_data)

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str) -> None:
        """Delete specified subscription."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]

        subscription_data = None
        for subscription in newsfeed_subscriptions_storage:
            if subscription['id'] == subscription_id:
                subscription_data = subscription
                break

        if subscription_data is None:
            raise SubscriptionNotFound(
                newsfeed_id=newsfeed_id,
                subscription_id=subscription_id,
            )

        to_newsfeed_id = str(subscription_data['to_newsfeed_id'])
        newsfeed_subscribers_storage = self._subscribers_storage[to_newsfeed_id]

        newsfeed_subscribers_storage.remove(subscription_data)
        newsfeed_subscriptions_storage.remove(subscription_data)


class RedisSubscriptionStorage(SubscriptionStorage):
    """Subscription storage that stores subscriptions in redis."""

    def __init__(self, config: Dict[str, str]):
        """Initialize queue."""
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

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> Iterable[SubscriptionData]:
        """Return subscriptions of specified newsfeed."""
        subscriptions_storage = []
        async with self._get_connection() as redis:
            for subscription in await redis.lrange(
                    key=f'subscriptions:{newsfeed_id}',
                    start=0,
                    stop=-1,
            ):
                subscriptions_storage.append(json.loads(subscription))
        return subscriptions_storage

    async def get_by_to_newsfeed_id(self, newsfeed_id: str) -> Iterable[SubscriptionData]:
        """Return subscriptions to specified newsfeed."""
        subscribers_storage = []
        async with self._get_connection() as redis:
            for subscriber in await redis.lrange(
                    key=f'subscribers:{newsfeed_id}',
                    start=0,
                    stop=-1,
            ):
                subscribers_storage.append(json.loads(subscriber))
        return subscribers_storage

    async def get_by_fqid(self, newsfeed_id: str, subscription_id: str) -> SubscriptionData:
        """Return subscription of specified newsfeed."""
        async with self._get_connection() as redis:
            subscription = await redis.get(f'subscription:{subscription_id}')

        if not subscription:
            raise SubscriptionNotFound(
                newsfeed_id=newsfeed_id,
                subscription_id=subscription_id,
            )

        return json.loads(subscription)

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str) -> SubscriptionData:
        """Return subscription between specified newsfeeds."""
        async with self._get_connection() as redis:
            subscription = await redis.get(
                f'subscription_between:{newsfeed_id}{to_newsfeed_id}'
            )

        if not subscription:
            raise SubscriptionBetweenNotFound(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )

        return json.loads(subscription)

    async def add(self, subscription_data: SubscriptionData) -> None:
        """Add subscription data to the storage."""
        subscription_id = str(subscription_data['id'])
        newsfeed_id = str(subscription_data['newsfeed_id'])
        to_newsfeed_id = str(subscription_data['to_newsfeed_id'])

        async with self._get_connection() as redis:
            await redis.lpush(
                key=f'subscriptions:{newsfeed_id}',
                value=json.dumps(subscription_data),
            )
            await redis.lpush(
                key=f'subscribers:{to_newsfeed_id}',
                value=json.dumps(subscription_data),
            )
            await redis.append(
                key=f'subscription:{subscription_id}',
                value=json.dumps(subscription_data),
            )
            await redis.append(
                key=f'subscription_between:{newsfeed_id}{to_newsfeed_id}',
                value=json.dumps(subscription_data),
            )

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str) -> None:
        """Delete specified subscription."""
        async with self._get_connection() as redis:
            subscription_key = f'subscription:{subscription_id}'
            subscription = await redis.get(subscription_key)

            if not subscription:
                raise SubscriptionNotFound(
                    newsfeed_id=newsfeed_id,
                    subscription_id=subscription_id,
                )

            subscription_data = json.loads(subscription)
            to_newsfeed_id = subscription_data['to_newsfeed_id']
            subscriptions = f'subscriptions:{newsfeed_id}'
            subscribers = f'subscribers:{to_newsfeed_id}'
            subscription_between = \
                f'subscription_between:{newsfeed_id}{to_newsfeed_id}'

            await redis.lrem(subscriptions, 1, subscription)
            await redis.lrem(subscribers, 1, subscription)
            await redis.delete(subscription_between)
            await redis.delete(subscription_key)

    @asynccontextmanager
    async def _get_connection(self) -> aioredis.commands.Redis:
        async with self._pool.get() as connection:
            redis = aioredis.commands.Redis(connection)
            yield redis


class SubscriptionStorageError(Exception):
    """Subscription-storage-related error."""

    @property
    def message(self) -> str:
        """Return error message."""
        return 'Newsfeed subscription storage error'


class SubscriptionNotFound(SubscriptionStorageError):
    """Error indicating situations when subscription could not be found in the storage."""

    def __init__(self, newsfeed_id: str, subscription_id: str):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._subscription_id = subscription_id

    @property
    def message(self) -> str:
        """Return error message."""
        return (
            f'Subscription "{self._subscription_id}" could not be found in newsfeed '
            f'"{self._newsfeed_id}"'
        )


class SubscriptionBetweenNotFound(SubscriptionStorageError):
    """Error indicating situations when subscription between newsfeeds could not be found."""

    def __init__(self, newsfeed_id: str, to_newsfeed_id: str):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._to_newsfeed_id = to_newsfeed_id

    @property
    def message(self) -> str:
        """Return error message."""
        return (
            f'Subscription from newsfeed "{self._newsfeed_id}" to "{self._to_newsfeed_id}" '
            f'could not be found'
        )


class NewsfeedNumberLimitExceeded(SubscriptionStorageError):
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


class SubscriptionNumberLimitExceeded(SubscriptionStorageError):
    """Error indicating situations when number of subscriptions per newsfeed exceeds maximum."""

    def __init__(self, subscription_id: str, newsfeed_id: str, to_newsfeed_id: str,
                 max_subscriptions_per_newsfeed: int):
        """Initialize error."""
        self._subscription_id = subscription_id
        self._newsfeed_id = newsfeed_id
        self._to_newsfeed_id = to_newsfeed_id
        self._max_subscriptions_per_newsfeed = max_subscriptions_per_newsfeed

    @property
    def message(self) -> str:
        """Return error message."""
        return (
            f'Subscriptions "{self._subscription_id}" from newsfeed {self._newsfeed_id} to '
            f'{self._to_newsfeed_id} could not be added to the storage because limit of '
            f'subscriptions per newsfeed exceeds maximum {self._max_subscriptions_per_newsfeed}'
        )
