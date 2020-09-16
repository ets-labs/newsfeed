"""Application test fixtures."""

from pytest import fixture

from newsfeed.containers import Container
from newsfeed.routes import setup_routes


@fixture
def container():
    return Container(
        config={
            'infrastructure': {
                'event_queue': {
                    'max_size': 1,
                },
                'event_storage': {
                    'max_newsfeeds': 3,
                    'max_events_per_newsfeed': 5,
                },
                'subscription_storage': {
                    'max_newsfeeds': 3,
                    'max_subscriptions_per_newsfeed': 5,
                },
            },
            'domainmodel': {
                'newsfeed_id_length': 16,
                'processor_concurrency': 1,
            },
            'webapi': {
                'base_path': '/',
            },
        },
    )


@fixture
def web_app(container):
    web_app = container.web_app()
    setup_routes(web_app, container)
    return web_app


@fixture
async def web_client(aiohttp_client, web_app):
    return await aiohttp_client(web_app)
