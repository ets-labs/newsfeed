"""Event loop module."""

import asyncio
import logging


logger = logging.getLogger(__name__)


def configure_event_loop(enable_uvloop: bool) -> None:
    """Configure event loop."""
    if enable_uvloop:
        try:
            import uvloop
        except ImportError:
            logger.warning('Uvloop is not installed')
            policy = asyncio.get_event_loop_policy()
        else:
            policy = uvloop.EventLoopPolicy()
    else:
        policy = asyncio.get_event_loop_policy()

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        ...
    else:
        running_loop.close()

    asyncio.set_event_loop_policy(policy)
    logger.debug(
        'Event loop policy set: %s.%s',
        policy.__class__.__module__,
        policy.__class__.__name__,
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.debug(
        'Event loop initialized: %s.%s',
        loop.__class__.__module__,
        loop.__class__.__name__,
    )
