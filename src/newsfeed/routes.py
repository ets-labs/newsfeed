"""Routes module."""

from aiohttp import web

from .containers import Container


def setup_routes(app: web.Application, container: Container) -> None:
    app.add_routes([
        # Subscriptions

        web.get(
            path='/newsfeed/{newsfeed_id}/subscriptions/',
            handler=container.get_subscriptions_view.as_view(),
        ),
        web.post(
            path='/newsfeed/{newsfeed_id}/subscriptions/',
            handler=container.add_subscription_view.as_view(),
        ),
        web.delete(
            path='/newsfeed/{newsfeed_id}/subscriptions/{subscription_id}/',
            handler=container.delete_subscription_view.as_view(),
        ),
        web.get(
            path='/newsfeed/{newsfeed_id}/subscribers/subscriptions/',
            handler=container.get_subscribers_view.as_view(),
        ),

        # Events

        web.get(
            path='/newsfeed/{newsfeed_id}/events/',
            handler=container.get_events_view.as_view(),
        ),
        web.post(
            path='/newsfeed/{newsfeed_id}/events/',
            handler=container.add_event_view.as_view(),
        ),
        web.delete(
            path='/newsfeed/{newsfeed_id}/events/{event_id}/',
            handler=container.delete_event_view.as_view(),
        ),

        # Miscellaneous

        web.get(
            path='/status/',
            handler=container.get_status_view.as_view(),
        ),
        web.get(
            path='/docs/',
            handler=container.get_docs_handler.as_view(),
        ),
    ])
