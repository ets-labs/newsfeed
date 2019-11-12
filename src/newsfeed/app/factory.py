"""Factory module."""

from dependency_injector import providers

from .application import Application
from .containers import Core, Infrastructure, DomainModel, WebApi
from .configuration import (
    get_core_config,
    get_infrastructure_config,
    get_domain_model_config,
    get_web_api_config,
)


application_factory = providers.Factory(
    Application,
    core=providers.Factory(
        Core,
        config=get_core_config(),
    ),
    infrastructure=providers.Factory(
        Infrastructure,
        config=get_infrastructure_config(),
    ),
    domain_model=providers.Factory(
        DomainModel,
        config=get_domain_model_config(),
    ),
    web_api=providers.Factory(
        WebApi,
        config=get_web_api_config(),
    ),
)
