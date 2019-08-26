"""Event handlers."""

from aiohttp import web


async def post_event_handler(_):
    """Handle events posing requests."""
    return web.json_response(
        status=202,
        data={
            'id': '<new_event_id>',
        },
    )
