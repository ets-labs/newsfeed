"""Utils module for infrastructure."""

from typing import Any, Dict
from urllib.parse import urlparse, parse_qsl

DEFAULT_REDIS_PORT = 6379


def parse_redis_dsn(dsn: str) -> Dict[str, Any]:
    """Redis dsn parser."""
    parsed_dsn = urlparse(dsn)
    assert parsed_dsn.scheme == 'redis', ('Unsupported URI scheme', parsed_dsn.scheme)
    return {
        'address': (parsed_dsn.hostname, int(parsed_dsn.port or DEFAULT_REDIS_PORT)),
        **dict(parse_qsl(parsed_dsn.query))
    }
