"""Infrastructure subscription storage module."""

from collections import defaultdict, deque
from typing import Mapping


class SubscriptionStorage:
    """Subscription storage."""

    def __init__(self, config):
        """Initialize storage."""
        self._config = config

    async def add(self, subscription_data: Mapping):
        """Add subscription data to the storage."""
        raise NotImplementedError()

    async def get_by_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions of specified newsfeed."""
        raise NotImplementedError()

    async def get_by_to_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions to specified newsfeed."""
        raise NotImplementedError()

    async def get(self, newsfeed_id: str, subscription_id: str):
        """Return subscription of specified newsfeed."""
        raise NotImplementedError()

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str):
        """Return subscription between specified newsfeeds."""
        raise NotImplementedError()

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str):
        """Delete specified subscription."""
        raise NotImplementedError()


class AsyncInMemorySubscriptionStorage(SubscriptionStorage):
    """Async subscription storage that stores subscriptions in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._subscriptions_storage = defaultdict(deque)
        self._subscribers_storage = defaultdict(deque)

    async def add(self, subscription_data: Mapping):
        """Add subscription data to the storage."""
        newsfeed_id = subscription_data['newsfeed_id']
        to_newsfeed_id = subscription_data['to_newsfeed_id']

        self._subscriptions_storage[newsfeed_id].appendleft(subscription_data)
        self._subscribers_storage[to_newsfeed_id].appendleft(subscription_data)

    async def get_by_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions of specified newsfeed."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        return list(newsfeed_subscriptions_storage)

    async def get_by_to_newsfeed_id(self, newsfeed_id: str):
        """Return subscriptions to specified newsfeed."""
        newsfeed_subscribers_storage = self._subscribers_storage[newsfeed_id]
        return list(newsfeed_subscribers_storage)

    async def get(self, newsfeed_id: str, subscription_id: str):
        """Return subscription of specified newsfeed."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        for subscription_data in newsfeed_subscriptions_storage:
            if subscription_data['id'] == subscription_id:
                return subscription_data
        else:
            raise RuntimeError(
                f'Newsfeed "{newsfeed_id}" subscription "{subscription_id}" could not be found',
            )

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str):
        """Return subscription between specified newsfeeds."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        for subscription_data in newsfeed_subscriptions_storage:
            if subscription_data['to_newsfeed_id'] == to_newsfeed_id:
                return subscription_data
        else:
            raise RuntimeError(
                f'Newsfeed "{newsfeed_id}" subscription to newsfeed "{to_newsfeed_id}" could not '
                f'be found',
            )

    async def delete_by_fqid(self, newsfeed_id: str, subscription_id: str):
        """Delete specified subscription."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]

        subscription_data = None
        for subscription in newsfeed_subscriptions_storage:
            if subscription['id'] == subscription_id:
                subscription_data = subscription
                break

        if subscription_data is None:
            return

        to_newsfeed_id = subscription_data['to_newsfeed_id']
        newsfeed_subscribers_storage = self._subscribers_storage[to_newsfeed_id]

        newsfeed_subscribers_storage.remove(subscription_data)
        newsfeed_subscriptions_storage.remove(subscription_data)
