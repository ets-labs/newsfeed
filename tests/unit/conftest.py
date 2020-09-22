"""Application test fixtures."""

from pytest import fixture

from newsfeed.app import create_app


@fixture
def app():
    app = create_app()
    yield app
    app.container.unwire()


@fixture
def container(app):
    return app.container


@fixture
async def web_client(aiohttp_client, app):
    return await aiohttp_client(app)
