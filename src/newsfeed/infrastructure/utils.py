"""Utils module for infrastructure."""

from typing import Any, Dict
from urllib.parse import urlparse, parse_qsl


def parse_redis_dsn(dsn: str) -> Dict[str, Any]:
    """Redis dsn parser."""
    parsed_dsn = urlparse(dsn)
    assert parsed_dsn.scheme == 'redis', ('Unsupported URI scheme', parsed_dsn.scheme)
    return {
        'address': (parsed_dsn.hostname, int(parsed_dsn.port)),
        **dict(parse_qsl(parsed_dsn.query))
    }
