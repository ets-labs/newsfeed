"""Event handlers."""

from aiohttp import web

from newsfeed.packages.domain_model.events import EventDispatcherService
from newsfeed.packages.domain_model.events import EventRepository


async def post_event_handler(request, *,
                             event_dispatcher_service: EventDispatcherService):
    """Handle events posting requests."""
    data = await request.json()

    await event_dispatcher_service.dispatch_event(event_data=data)

    return web.json_response(
        status=202,
        data={
            'id': '<new_event_id>',
        },
    )


async def get_events_handler(request, *,
                             event_repository: EventRepository):
    """Handle events getting requests."""
    newsfeed_id = request.query['newsfeed_id']

    newsfeed_events = await event_repository.get_newsfeed(newsfeed_id)

    return web.json_response(
        data={
            'results': newsfeed_events,
        },
    )
