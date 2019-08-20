"""Miscellaneous handlers."""

from aiohttp import web


async def get_status_handler(_):
    """Handle status requests."""
    return web.json_response({'status': 'OK'})
