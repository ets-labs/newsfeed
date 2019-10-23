"""Factory module."""

from dependency_injector import providers

from .application import Application
from .containers import Infrastructure, DomainModel, WebApi
from .configuration import get_infrastructure_config, get_domain_model_config, get_web_api_config


application_factory = providers.Factory(
    Application,
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
