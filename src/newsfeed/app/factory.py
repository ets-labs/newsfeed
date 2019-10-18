"""Factory module."""

import os

from dependency_injector import providers

from .application import Application
from .containers import Infrastructure, DomainModel, WebApi


application_factory = providers.Factory(
    Application,
    infrastructure=providers.Factory(
        Infrastructure,
        config={
            'event_queue': {
                'max_size': os.getenv('EVENTS_QUEUE_SIZE'),
            },
            'event_storage': {
                'max_newsfeeds': os.getenv('MAX_NEWSFEEDS'),
                'max_events_per_newsfeed': os.getenv('EVENTS_PER_NEWSFEED'),
            },
            'subscription_storage': {
                'max_newsfeeds': os.getenv('MAX_NEWSFEEDS'),
                'max_subscriptions_per_newsfeed': os.getenv('SUBSCRIPTIONS_PER_NEWSFEED'),
            },
        },
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
