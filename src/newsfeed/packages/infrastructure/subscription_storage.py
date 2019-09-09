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


class AsyncInMemorySubscriptionStorage(SubscriptionStorage):
    """Async subscription storage that stores subscriptions in memory."""

    def __init__(self, config):
        """Initialize queue."""
        super().__init__(config)
        self._storage = defaultdict(deque)

    async def add(self, subscription_data):
        """Add subscription data to the storage."""
        to_newsfeed_id = subscription_data['to_newsfeed_id']
        newsfeed_subscriptions_storage = self._storage[to_newsfeed_id]
        newsfeed_subscriptions_storage.appendleft(subscription_data)
