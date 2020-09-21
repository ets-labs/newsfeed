"""Application configuration module."""

import os
from typing import Dict, Optional, Any


def get_config() -> Dict[str, Any]:
    """Return application configuration."""
    return {
        'core': {
            'log_level': os.getenv('LOG_LEVEL'),
            'enable_uvloop': _bool(os.getenv('ENABLE_UVLOOP')),
        },
        'infrastructure': {
            'event_queue': {
                'max_size': os.getenv('EVENTS_QUEUE_SIZE'),
            },
            'event_storage': {
                'max_newsfeeds': os.getenv('MAX_NEWSFEEDS'),
                'max_events_per_newsfeed': os.getenv('EVENTS_PER_NEWSFEED'),
                'dsn': os.getenv('EVENT_STORAGE_DSN'),
            },
            'subscription_storage': {
                'max_newsfeeds': os.getenv('MAX_NEWSFEEDS'),
                'max_subscriptions_per_newsfeed': os.getenv('SUBSCRIPTIONS_PER_NEWSFEED'),
            },
        },
        'domain': {
            'newsfeed_id_length': os.getenv('NEWSFEED_ID_LENGTH'),
            'processor_concurrency': os.getenv('PROCESSOR_CONCURRENCY'),
        },
        'webapi': {
            'port': os.getenv('PORT'),
            'base_path': os.getenv('API_BASE_PATH'),
        },
    }


def _bool(value: Optional[str]) -> bool:
    if not value:
        return False
    return str(value).lower() in ('true', '1')
