"""Subscriptions module."""

from typing import Type

from newsfeed.packages.infrastructure.subscription_storage import SubscriptionStorage


class Subscription:
    """Subscription entity."""


class SubscriptionFactory:
    """Subscription entity factory."""

    def __init__(self, cls: Type[Subscription]):
        """Initialize factory."""
        assert issubclass(cls, Subscription)
        self._cls = cls


class SubscriptionSpecification:
    """Subscription specification."""

    def __init__(self):
        """Initialize specification."""


class SubscriptionRepository:
    """Subscription repository."""

    def __init__(self, factory: SubscriptionFactory, storage: SubscriptionStorage):
        """Initialize repository."""
        assert isinstance(factory, SubscriptionFactory)
        self._factory = factory

        assert isinstance(storage, SubscriptionStorage)
        self._storage = storage


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
