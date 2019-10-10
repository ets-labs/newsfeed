"""Subscription handlers."""

from aiohttp import web

from newsfeed.packages.domain_model.subscription import SubscriptionService, Subscription


async def post_subscription_handler(request, *,
                                    subscription_service: SubscriptionService):
    """Handle subscriptions posting requests."""
    data = await request.json()

    subscription = await subscription_service.create_subscription(
        newsfeed_id=request.match_info['newsfeed_id'],
        to_newsfeed_id=data['to_newsfeed_id'],
    )

    return web.json_response(
        status=200,
        data=_serialize_subscription(subscription),
    )


async def get_subscriptions_handler(request, *,
                                    subscription_service: SubscriptionService):
    """Handle subscriptions getting requests."""
    newsfeed_subscriptions = await subscription_service.get_newsfeed_subscriptions(
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


async def get_subscriber_subscriptions_handler(request, *,
                                               subscription_service: SubscriptionService):
    """Handle subscriber subscriptions getting requests."""
    newsfeed_subscriptions = await subscription_service.get_newsfeed_subscriber_subscriptions(
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


async def delete_subscription_handler(request, *,
                                      subscription_service: SubscriptionService):
    """Handle subscriptions deleting requests."""
    await subscription_service.delete_newsfeed_subscription(
        newsfeed_id=request.match_info['newsfeed_id'],
        subscription_id=request.match_info['subscription_id'],
    )
    return web.json_response(status=204)


def _serialize_subscription(subscription: Subscription):
    return {
        'id': str(subscription.id),
        'from_newsfeed_id': str(subscription.from_newsfeed_id),
        'to_newsfeed_id': str(subscription.to_newsfeed_id),
        'subscribed_at': int(subscription.subscribed_at.timestamp()),
    }
