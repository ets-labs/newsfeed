"""Application test fixtures."""

from pytest import fixture

from newsfeed.app import application


@fixture
def app():
    """Create test application."""
    return application.Application()


@fixture
def infrastructure(app):
    """Return infrastructure container."""
    return app.infrastructure


@fixture
def domain_model(app):
    """Return domain model container."""
    return app.domain_model


@fixture
def web_app(app):
    """Create test web application."""
    return app.web_api.web_app()


@fixture
async def web_client(aiohttp_client, web_app):
    """Create test application client."""
    return await aiohttp_client(web_app)
