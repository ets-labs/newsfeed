"""Application test fixtures."""

from pytest import fixture

from newsfeed.app import application


@fixture
def web_app():
    """Create test web application."""
    app = application.Application()
    web_app = app.create_web_app()

    return web_app


@fixture
def infrastructure(web_app):
    """Return infrastructure container."""
    return web_app.infrastructure


@fixture
def domain_model(web_app):
    """Return domain model container."""
    return web_app.domain_model


@fixture
async def web_client(aiohttp_client, web_app):
    """Create test application client."""
    return await aiohttp_client(web_app)
