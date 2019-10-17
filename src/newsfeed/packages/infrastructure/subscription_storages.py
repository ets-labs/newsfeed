"""Infrastructure subscription storages module."""

from collections import defaultdict, deque
from typing import Mapping


class SubscriptionStorage:
    """Subscription storage."""

    def __init__(self, config):
        """Initialize storage."""
        self._config = config

    async def get_by_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions of specified newsfeed."""
        raise NotImplementedError()

    async def get_by_to_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions to specified newsfeed."""
        raise NotImplementedError()

    async def get_by_fqid(self, newsfeed_id: str, subscription_id: str):
        """Return subscription of specified newsfeed."""
        raise NotImplementedError()

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str):
        """Return subscription between specified newsfeeds."""
        raise NotImplementedError()

    async def add(self, subscription_data: Mapping):
        """Add subscription data to the storage."""
        raise NotImplementedError()

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str):
        """Delete specified subscription."""
        raise NotImplementedError()


class InMemorySubscriptionStorage(SubscriptionStorage):
    """Subscription storage that stores subscriptions in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._subscriptions_storage = defaultdict(deque)
        self._subscribers_storage = defaultdict(deque)

    async def get_by_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions of specified newsfeed."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        return list(newsfeed_subscriptions_storage)

    async def get_by_to_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions to specified newsfeed."""
        newsfeed_subscribers_storage = self._subscribers_storage[newsfeed_id]
        return list(newsfeed_subscribers_storage)

    async def get_by_fqid(self, newsfeed_id: str, subscription_id: str):
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

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str):
        """Return subscription between specified newsfeeds."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        for subscription_data in newsfeed_subscriptions_storage:
            if subscription_data['to_newsfeed_id'] == to_newsfeed_id:
                return subscription_data
        else:
            raise SubscriptionBetweenNotFound(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )

    async def add(self, subscription_data: Mapping):
        """Add subscription data to the storage."""
        newsfeed_id = subscription_data['newsfeed_id']
        to_newsfeed_id = subscription_data['to_newsfeed_id']

        self._subscriptions_storage[newsfeed_id].appendleft(subscription_data)
        self._subscribers_storage[to_newsfeed_id].appendleft(subscription_data)

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str):
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

        to_newsfeed_id = subscription_data['to_newsfeed_id']
        newsfeed_subscribers_storage = self._subscribers_storage[to_newsfeed_id]

        newsfeed_subscribers_storage.remove(subscription_data)
        newsfeed_subscriptions_storage.remove(subscription_data)


class SubscriptionStorageError(Exception):
    """Subscription-storage-related error."""

    @property
    def message(self):
        """Return error message."""
        return 'Newsfeed subscription storage error'


class SubscriptionNotFound(SubscriptionStorageError):
    """Error indicating situations when subscription could not be found in the storage."""

    def __init__(self, newsfeed_id, subscription_id):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._subscription_id = subscription_id

    @property
    def message(self):
        """Return error message."""
        return (
            f'Subscription "{self._subscription_id}" could not be found in newsfeed '
            f'"{self._newsfeed_id}"'
        )


class SubscriptionBetweenNotFound(SubscriptionStorageError):
    """Error indicating situations when subscription between newsfeeds could not be found."""

    def __init__(self, newsfeed_id, to_newsfeed_id):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._to_newsfeed_id = to_newsfeed_id

    @property
    def message(self):
        """Return error message."""
        return (
            f'Subscription from newsfeed "{self._newsfeed_id}" to "{self._to_newsfeed_id}" '
            f'could not be found'
        )
