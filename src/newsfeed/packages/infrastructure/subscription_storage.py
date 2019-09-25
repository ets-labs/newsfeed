"""Infrastructure subscription storage module."""

from collections import defaultdict, deque


class SubscriptionStorage:
    """Subscription storage."""

    def __init__(self, config):
        """Initialize storage."""
        self._config = config

    async def add(self, subscription_data):
        """Add subscription data to the storage."""
        raise NotImplementedError()

    async def get_from(self, newsfeed_id):
        """Return subscriptions of specified newsfeed."""
        raise NotImplementedError()

    async def get_to(self, newsfeed_id):
        """Return subscriptions to specified newsfeed."""
        raise NotImplementedError()


class AsyncInMemorySubscriptionStorage(SubscriptionStorage):
    """Async subscription storage that stores subscriptions in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._subscriptions_storage = defaultdict(deque)
        self._subscribers_storage = defaultdict(deque)

    async def add(self, subscription_data):
        """Add subscription data to the storage."""
        from_newsfeed_id = subscription_data['from_newsfeed_id']
        to_newsfeed_id = subscription_data['to_newsfeed_id']

        self._subscriptions_storage[from_newsfeed_id].appendleft(subscription_data)
        self._subscribers_storage[to_newsfeed_id].appendleft(subscription_data)

    async def get_from(self, newsfeed_id):
        """Return subscriptions of specified newsfeed."""
        newsfeed_subscriptions_storage = self._subscriptions_storage[newsfeed_id]
        return list(newsfeed_subscriptions_storage)

    async def get_to(self, newsfeed_id):
        """Return subscriptions to specified newsfeed."""
        newsfeed_subscribers_storage = self._subscribers_storage[newsfeed_id]
        return list(newsfeed_subscribers_storage)
