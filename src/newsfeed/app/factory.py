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
        config={
            'newsfeed_id_length': os.getenv('NEWSFEED_ID_LENGTH'),
        },
    ),
    web_api=providers.Factory(
        WebApi,
        config={
            'port': os.getenv('PORT'),
            'base_path': os.getenv('API_BASE_PATH'),
        },
    ),
    processor_concurrency=os.getenv('PROCESSOR_CONCURRENCY'),
)
