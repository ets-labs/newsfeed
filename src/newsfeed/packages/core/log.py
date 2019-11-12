"""Logging module."""

import logging.config


def configure_logging(level: str) -> None:
    """Configure logging."""
    logging.config.dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'level': level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                },
            },
            'loggers': {
                '': {
                    'level': level,
                    'handlers': ['console'],
                    'propagate': False
                },
                'aiohttp': {
                    'level': level,
                    'handlers': ['console'],
                    'propagate': False
                },
                'aiohttp.access': {
                    'propagate': False,
                },
            },
        },
    )
