"""Event handlers."""

from aiohttp import web

from newsfeed.packages.domain_model.events import EventDispatcherService


async def post_event_handler(request, *,
                             event_dispatcher_service: EventDispatcherService):
    """Handle events posing requests."""
    data = await request.json()

    await event_dispatcher_service.dispatch_event(event_data=data)

    return web.json_response(
        status=202,
        data={
            'id': '<new_event_id>',
        },
    )
