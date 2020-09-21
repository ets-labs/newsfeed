"""Subscriptions module."""

from __future__ import annotations

from typing import Dict, List, Tuple, Any
from uuid import UUID, uuid4
from datetime import datetime

from newsfeed.infrastructure.subscription_storages import (
    SubscriptionStorage,
    SubscriptionBetweenNotFound,
)
from .newsfeed_id import NewsfeedIDSpecification
from .error import DomainError


class SubscriptionFQID:
    """Subscription fully-qualified identifier."""

    def __init__(self, newsfeed_id: str, subscription_id: UUID):
        """Initialize object."""
        assert isinstance(newsfeed_id, str)
        self.newsfeed_id = newsfeed_id

        assert isinstance(subscription_id, UUID)
        self.subscription_id = subscription_id

    @classmethod
    def from_serialized_data(cls, data: Tuple[str, str]) -> SubscriptionFQID:
        """Create instance from serialized data."""
        return cls(data[0], UUID(data[1]))

    @property
    def serialized_data(self) -> Tuple[str, str]:
        """Return serialized data."""
        return self.newsfeed_id, str(self.subscription_id)


class Subscription:
    """Subscription entity."""

    def __init__(self, id: UUID, newsfeed_id: str, to_newsfeed_id: str, subscribed_at: datetime):
        """Initialize entity."""
        assert isinstance(id, UUID)
        self._id = id

        assert isinstance(newsfeed_id, str)
        self._newsfeed_id = newsfeed_id

        assert isinstance(to_newsfeed_id, str)
        self._to_newsfeed_id = to_newsfeed_id

        assert isinstance(subscribed_at, datetime)
        self._subscribed_at = subscribed_at

    @property
    def id(self) -> UUID:
        """Return id."""
        return self._id

    @property
    def newsfeed_id(self) -> str:
        """Return newsfeed id."""
        return self._newsfeed_id

    @property
    def to_newsfeed_id(self) -> str:
        """Return to newsfeed id."""
        return self._to_newsfeed_id

    @property
    def fqid(self) -> SubscriptionFQID:
        """Return FQID (Fully-Qualified ID)."""
        return SubscriptionFQID(self.newsfeed_id, self.id)

    @property
    def subscribed_at(self) -> datetime:
        """Return subscribed at."""
        return self._subscribed_at

    @property
    def serialized_data(self) -> Dict[str, Any]:
        """Return serialized data."""
        return {
            'id': str(self._id),
            'newsfeed_id': self._newsfeed_id,
            'to_newsfeed_id': self._to_newsfeed_id,
            'subscribed_at': self._subscribed_at.timestamp(),
        }

    @classmethod
    def create_from_serialized(cls, data: Dict[str, Any]) -> Subscription:
        """Create instance from serialized data."""
        return cls(
            id=UUID(data['id']),
            newsfeed_id=data['newsfeed_id'],
            to_newsfeed_id=data['to_newsfeed_id'],
            subscribed_at=datetime.utcfromtimestamp(data['subscribed_at']),
        )


class SubscriptionFactory:
    """Subscription entity factory."""

    cls = Subscription

    def create_new(self, newsfeed_id: str, to_newsfeed_id: str) -> Subscription:
        """Create new instance."""
        return self.cls(
            id=uuid4(),
            newsfeed_id=newsfeed_id,
            to_newsfeed_id=to_newsfeed_id,
            subscribed_at=datetime.utcnow(),
        )

    def create_from_serialized(self, data: Dict[str, Any]) -> Subscription:
        """Create instance from serialized data."""
        return self.cls.create_from_serialized(data)


class SubscriptionSpecification:
    """Subscription specification."""

    def __init__(self, newsfeed_id_specification: NewsfeedIDSpecification):
        """Initialize specification."""
        self._newsfeed_id_specification = newsfeed_id_specification

    def is_satisfied_by(self, subscription: Subscription) -> bool:
        """Check if subscription satisfies specification."""
        self._newsfeed_id_specification.is_satisfied_by(subscription.newsfeed_id)
        self._newsfeed_id_specification.is_satisfied_by(subscription.to_newsfeed_id)

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

    async def get_by_newsfeed_id(self, newsfeed_id: str) -> List[Subscription]:
        """Return subscriptions of specified newsfeed."""
        subscriptions_data = await self._storage.get_by_newsfeed_id(newsfeed_id)
        return [
            self._factory.create_from_serialized(subscription_data)
            for subscription_data in subscriptions_data
        ]

    async def get_by_to_newsfeed_id(self, newsfeed_id: str) -> List[Subscription]:
        """Return subscriptions to specified newsfeed."""
        subscriptions_data = await self._storage.get_by_to_newsfeed_id(newsfeed_id)
        return [
            self._factory.create_from_serialized(subscription_data)
            for subscription_data in subscriptions_data
        ]

    async def get_by_fqid(self, newsfeed_id: str, subscription_id: UUID) -> Subscription:
        """Return subscription by its FQID."""
        subscription_data = await self._storage.get_by_fqid(newsfeed_id, str(subscription_id))
        return self._factory.create_from_serialized(subscription_data)

    async def get_between(self, newsfeed_id: str, to_newsfeed_id: str) -> Subscription:
        """Return subscription between two newsfeeds."""
        subscription_data = await self._storage.get_between(newsfeed_id, to_newsfeed_id)
        return self._factory.create_from_serialized(subscription_data)

    async def add(self, subscription: Subscription) -> None:
        """Add subscription to repository."""
        await self._storage.add(subscription.serialized_data)

    async def delete_by_fqid(self, fqid: SubscriptionFQID) -> None:
        """Delete subscription by its FQID."""
        await self._storage.delete_by_fqid(
            newsfeed_id=fqid.newsfeed_id,
            subscription_id=str(fqid.subscription_id),
        )


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

    async def get_subscriptions(self, newsfeed_id: str) -> List[Subscription]:
        """Return list of newsfeed subscriptions."""
        return await self._repository.get_by_newsfeed_id(newsfeed_id)

    async def get_subscriber_subscriptions(self, newsfeed_id: str) -> List[Subscription]:
        """Return list of newsfeed subscriber subscriptions."""
        return await self._repository.get_by_to_newsfeed_id(newsfeed_id)

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

    async def delete_subscription(self, newsfeed_id: str, subscription_id: str) -> None:
        """Delete newsfeed subscription."""
        subscription = await self._repository.get_by_fqid(newsfeed_id, UUID(subscription_id))
        await self._repository.delete_by_fqid(subscription.fqid)

    async def _check_subscription_exists_between(self, newsfeed_id: str, to_newsfeed_id: str) \
            -> bool:
        try:
            _ = await self._repository.get_between(
                newsfeed_id=newsfeed_id,
                to_newsfeed_id=to_newsfeed_id,
            )
        except SubscriptionBetweenNotFound:
            return False
        else:
            return True


class SubscriptionError(DomainError):
    """Subscription-related error."""

    @property
    def message(self) -> str:
        """Return error message."""
        return 'Newsfeed subscription error'


class SelfSubscriptionError(SubscriptionError):
    """Error indicating situations when subscription of newsfeed to itself is attempted."""

    def __init__(self, newsfeed_id: str):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id

    @property
    def message(self) -> str:
        """Return error message."""
        return f'Subscription of newsfeed "{self._newsfeed_id}" to itself is restricted'


class SubscriptionAlreadyExistsError(SubscriptionError):
    """Error indicating situations when subscription between two newsfeeds already exists."""

    def __init__(self, newsfeed_id: str, to_newsfeed_id: str):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._to_newsfeed_id = to_newsfeed_id

    @property
    def message(self) -> str:
        """Return error message."""
        return (
            f'Subscription from newsfeed "{self._newsfeed_id}" to "{self._to_newsfeed_id}" '
            f'already exists'
        )
