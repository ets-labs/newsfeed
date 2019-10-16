"""Subscriptions module."""

from typing import Type, Sequence
from uuid import UUID, uuid4
from datetime import datetime

from newsfeed.packages.infrastructure.subscription_storage import SubscriptionStorage


class Subscription:
    """Subscription entity."""

    def __init__(self, id: UUID, newsfeed_id: str, to_newsfeed_id: str, subscribed_at):
        assert isinstance(id, UUID)
        self._id = id

        assert isinstance(newsfeed_id, str)
        self._newsfeed_id = newsfeed_id

        assert isinstance(to_newsfeed_id, str)
        self._to_newsfeed_id = to_newsfeed_id

        assert isinstance(subscribed_at, datetime)
        self._subscribed_at = subscribed_at

    @property
    def id(self):
        """Return id."""
        return self._id

    @property
    def newsfeed_id(self):
        """Return newsfeed id."""
        return self._newsfeed_id

    @property
    def to_newsfeed_id(self):
        """Return to newsfeed id."""
        return self._to_newsfeed_id

    @property
    def subscribed_at(self):
        """Return subscribed at."""
        return self._subscribed_at

    @property
    def serialized_data(self):
        """Return serialized data."""
        return {
            'id': str(self._id),
            'newsfeed_id': self._newsfeed_id,
            'to_newsfeed_id': self._to_newsfeed_id,
            'subscribed_at': self._subscribed_at.timestamp(),
        }


class SubscriptionFactory:
    """Subscription entity factory."""

    def __init__(self, cls: Type[Subscription]):
        """Initialize factory."""
        assert issubclass(cls, Subscription)
        self._cls = cls

    def create_new(self, newsfeed_id, to_newsfeed_id) -> Subscription:
        """Create new subscription."""
        return self._cls(
            id=uuid4(),
            newsfeed_id=newsfeed_id,
            to_newsfeed_id=to_newsfeed_id,
            subscribed_at=datetime.utcnow(),
        )

    def create_from_serialized(self, data) -> Subscription:
        """Create subscription from serialized data."""
        return self._cls(
            id=UUID(data['id']),
            newsfeed_id=data['newsfeed_id'],
            to_newsfeed_id=data['to_newsfeed_id'],
            subscribed_at=datetime.utcfromtimestamp(data['subscribed_at']),
        )


class SubscriptionSpecification:
    """Subscription specification."""

    def __init__(self):
        """Initialize specification."""

    def is_satisfied_by(self, subscription: Subscription):
        """Check if subscription satisfies specification."""
        if subscription.newsfeed_id == subscription.to_newsfeed_id:
            raise SelfSubscriptionError(newsfeed_id=subscription.newsfeed_id)
        return True


class SubscriptionRepository:
    """Subscription repository."""

    def __init__(self, factory: SubscriptionFactory, storage: SubscriptionStorage):
        """Initialize repository."""
        assert isinstance(factory, SubscriptionFactory)
        self._factory = factory

        assert isinstance(storage, SubscriptionStorage)
        self._storage = storage

    async def add(self, subscription: Subscription):
        """Add subscription to repository."""
        await self._storage.add(subscription.serialized_data)

    async def get_all(self, newsfeed_id: str):
        """Return subscriptions of specified newsfeed."""
        subscriptions_data = await self._storage.get_all(newsfeed_id)
        return [
            self._factory.create_from_serialized(subscription_data)
            for subscription_data in subscriptions_data
        ]

    async def get_all_to(self, newsfeed_id: str):
        """Return subscriptions to specified newsfeed."""
        subscriptions_data = await self._storage.get_all_to(newsfeed_id)
        return [
            self._factory.create_from_serialized(subscription_data)
            for subscription_data in subscriptions_data
        ]

    async def get_subscription(self, newsfeed_id: str, subscription_id: UUID) -> Subscription:
        """Return newsfeed subscription."""
        subscription_data = await self._storage.get(newsfeed_id, str(subscription_id))
        return self._factory.create_from_serialized(subscription_data)

    async def get_subscription_between(self, newsfeed_id: str, to_newsfeed_id: str) -> Subscription:  # noqa
        """Return subscription between two newsfeeds."""
        subscription_data = await self._storage.get_between(newsfeed_id, to_newsfeed_id)
        return self._factory.create_from_serialized(subscription_data)

    async def delete_subscription(self, subscription: Subscription):
        """Delete subscription."""
        await self._storage.delete(subscription.serialized_data)


class SubscriptionService:
    """Subscription service."""

    def __init__(self,
                 factory: SubscriptionFactory,
                 specification: SubscriptionSpecification,
                 repository: SubscriptionRepository):
        """Initialize service."""
        assert isinstance(factory, SubscriptionFactory)
        self._factory = factory

        assert isinstance(specification, SubscriptionSpecification)
        self._specification = specification

        assert isinstance(repository, SubscriptionRepository)
        self._repository = repository

    async def get_subscriptions(self, newsfeed_id: str) -> Sequence[Subscription]:
        """Return list of newsfeed subscriptions."""
        return await self._repository.get_all(newsfeed_id)

    async def get_subscriber_subscriptions(self, newsfeed_id: str) -> Sequence[Subscription]:
        """Return list of newsfeed subscriber subscriptions."""
        return await self._repository.get_all_to(newsfeed_id)

    async def create_subscription(self, newsfeed_id: str, to_newsfeed_id: str) -> Subscription:
        """Create subscription."""
        subscription_exists = await self._check_subscription_exists_between(
            newsfeed_id=newsfeed_id,
            to_newsfeed_id=to_newsfeed_id,
        )
        if subscription_exists:
            raise SubscriptionAlreadyExistsError(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )

        subscription = self._factory.create_new(
            newsfeed_id=newsfeed_id,
            to_newsfeed_id=to_newsfeed_id,
        )

        self._specification.is_satisfied_by(subscription)
        await self._repository.add(subscription)

        return subscription

    async def delete_subscription(self, newsfeed_id: str, subscription_id: str):
        """Delete newsfeed subscription."""
        subscription = await self._repository.get_subscription(newsfeed_id, UUID(subscription_id))
        await self._repository.delete_subscription(subscription)

    async def _check_subscription_exists_between(self, newsfeed_id, to_newsfeed_id):
        try:
            _ = await self._repository.get_subscription_between(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )
        except RuntimeError:
            return False
        else:
            return True


class SubscriptionError(Exception):
    """Subscription-related error."""

    @property
    def message(self):
        """Return error message."""
        return 'Newsfeed subscription error'


class SelfSubscriptionError(SubscriptionError):
    """Error indicating situations when subscription of newsfeed to itself is attempted."""

    def __init__(self, newsfeed_id):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id

    @property
    def message(self):
        """Return error message."""
        return f'Subscription of newsfeed "{self._newsfeed_id}" to itself is restricted'


class SubscriptionAlreadyExistsError(SubscriptionError):
    """Error indicating situations when subscription between two newsfeeds already exists."""

    def __init__(self, newsfeed_id, to_newsfeed_id):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._to_newsfeed_id = to_newsfeed_id

    @property
    def message(self):
        """Return error message."""
        return (
            f'Subscription from newsfeed "{self._newsfeed_id}" to "{self._to_newsfeed_id}" '
            f'already exists'
        )
