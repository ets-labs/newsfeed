"""Configuration module."""

import os
from typing import Dict, Optional


def get_infrastructure_config() -> Dict[str, Dict[str, Optional[str]]]:
    """Return infrastructure configuration."""
    return {
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
    }


def get_domain_model_config() -> Dict[str, Optional[str]]:
    """Return domain model configuration."""
    return {
        'newsfeed_id_length': os.getenv('NEWSFEED_ID_LENGTH'),
        'processor_concurrency': os.getenv('PROCESSOR_CONCURRENCY'),
    }


def get_web_api_config() -> Dict[str, Optional[str]]:
    """Return web API configuration."""
    return {
        'port': os.getenv('PORT'),
        'base_path': os.getenv('API_BASE_PATH'),
    }
