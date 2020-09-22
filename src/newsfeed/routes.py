"""Routes module."""

from aiohttp import web

from .handlers import subscriptions, events, misc


def setup_routes(app: web.Application) -> None:
    app.add_routes([
        # Subscriptions

        web.get(
            path='/newsfeed/{newsfeed_id}/subscriptions/',
            handler=subscriptions.get_subscriptions_handler,
        ),
        web.post(
            path='/newsfeed/{newsfeed_id}/subscriptions/',
            handler=subscriptions.post_subscription_handler,
        ),
        web.delete(
            path='/newsfeed/{newsfeed_id}/subscriptions/{subscription_id}/',
            handler=subscriptions.delete_subscription_handler,
        ),
        web.get(
            path='/newsfeed/{newsfeed_id}/subscribers/subscriptions/',
            handler=subscriptions.get_subscriber_subscriptions_handler,
        ),

        # Events

        web.get(
            path='/newsfeed/{newsfeed_id}/events/',
            handler=events.get_events_handler,
        ),
        web.post(
            path='/newsfeed/{newsfeed_id}/events/',
            handler=events.post_event_handler,
        ),
        web.delete(
            path='/newsfeed/{newsfeed_id}/events/{event_id}/',
            handler=events.delete_event_handler,
        ),

        # Miscellaneous

        web.get(
            path='/status/',
            handler=misc.get_status_handler,
        ),
        web.get(
            path='/docs/',
            handler=misc.get_openapi_schema_handler,
        ),
    ])
