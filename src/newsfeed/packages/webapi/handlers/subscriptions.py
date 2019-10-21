"""Subscription handlers."""

from typing import Dict, Union

from aiohttp import web

from newsfeed.packages.domain_model.subscription import (
    Subscription,
    SubscriptionService,
)
from newsfeed.packages.domain_model.error import DomainError


SerializedSubscription = Dict[
    str,
    Union[
        str,
        int,
    ],
]


async def get_subscriptions_handler(request: web.Request, *,
                                    subscription_service: SubscriptionService) -> web.Response:
    """Handle subscriptions getting requests."""
    newsfeed_subscriptions = await subscription_service.get_subscriptions(
        newsfeed_id=request.match_info['newsfeed_id'],
    )
    return web.json_response(
        data={
            'results': [
                _serialize_subscription(subscription)
                for subscription in newsfeed_subscriptions
            ],
        },
    )


async def post_subscription_handler(request: web.Request, *,
                                    subscription_service: SubscriptionService) -> web.Response:
    """Handle subscriptions posting requests."""
    data = await request.json()

    try:
        subscription = await subscription_service.create_subscription(
            newsfeed_id=request.match_info['newsfeed_id'],
            to_newsfeed_id=data['to_newsfeed_id'],
        )
    except DomainError as exception:
        return web.json_response(
            status=400,
            data={
                'message': exception.message,
            }
        )

    return web.json_response(
        status=200,
        data=_serialize_subscription(subscription),
    )


async def delete_subscription_handler(request: web.Request, *,
                                      subscription_service: SubscriptionService) -> web.Response:
    """Handle subscriptions deleting requests."""
    await subscription_service.delete_subscription(
        newsfeed_id=request.match_info['newsfeed_id'],
        subscription_id=request.match_info['subscription_id'],
    )
    return web.json_response(status=204)


async def get_subscriber_subscriptions_handler(request: web.Request, *,
                                               subscription_service: SubscriptionService) -> web.Response:  # noqa
    """Handle subscriber subscriptions getting requests."""
    newsfeed_subscriptions = await subscription_service.get_subscriber_subscriptions(
        newsfeed_id=request.match_info['newsfeed_id'],
    )
    return web.json_response(
        data={
            'results': [
                _serialize_subscription(subscription)
                for subscription in newsfeed_subscriptions
            ],
        },
    )


def _serialize_subscription(subscription: Subscription) -> SerializedSubscription:
    return {
        'id': str(subscription.id),
        'newsfeed_id': str(subscription.newsfeed_id),
        'to_newsfeed_id': str(subscription.to_newsfeed_id),
        'subscribed_at': int(subscription.subscribed_at.timestamp()),
    }
