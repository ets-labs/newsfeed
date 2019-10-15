"""Factory module."""

import os

from dependency_injector import providers

from .application import Application
from .containers import Infrastructure, DomainModel, WebApi


application_factory = providers.Factory(
    Application,
    infrastructure=providers.Factory(
        Infrastructure,
    ),
    domain_model=providers.Factory(
        DomainModel,
    ),
    web_api=providers.Factory(
        WebApi,
        config={
            'base_path': os.getenv('API_BASE_PATH'),
        },
    ),
)
