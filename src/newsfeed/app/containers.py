"""Containers module."""

from dependency_injector import containers, providers

from newsfeed.packages import domain, webapi


class DomainModel(containers.DeclarativeContainer):
    """Domain model container."""


class WebApi(containers.DeclarativeContainer):
    """Web API container."""

    domain: DomainModel = providers.DependenciesContainer()

    web_app = providers.Factory(
        webapi.app.create_web_app,
        routes=[
            # Miscellaneous
            webapi.app.route(
                method='GET',
                path='/status/',
                handler=providers.Coroutine(
                    webapi.handlers.misc.get_status_handler,
                ),
            ),
        ],
    )
