"""Subscription handlers."""

from aiohttp import web

from newsfeed.packages.domain_model.subscriptions import SubscriptionService


async def post_subscription_handler(request, *,
                                    subscription_service: SubscriptionService):
    """Handle events posting requests."""
    data = await request.json()

    subscription = await subscription_service.create_subscription(subscription_data=data)

    return web.json_response(
        status=200,
        data={
            'id': str(subscription.id),
        },
    )
