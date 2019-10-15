"""Event handlers."""

from aiohttp import web

from newsfeed.packages.domain_model.event import EventRepository
from newsfeed.packages.domain_model.event_dispatcher import EventDispatcherService


async def get_events_handler(request, *,
                             event_repository: EventRepository):
    """Handle events getting requests."""
    newsfeed_id = request.match_info['newsfeed_id']

    newsfeed_events = await event_repository.get_all_by_newsfeed_id(newsfeed_id)

    return web.json_response(
        data={
            'results': newsfeed_events,
        },
    )


async def post_event_handler(request, *,
                             event_dispatcher_service: EventDispatcherService):
    """Handle events posting requests."""
    event_data = await request.json()

    event = await event_dispatcher_service.dispatch_new_event_posting(
        newsfeed_id=request.match_info['newsfeed_id'],
        data=event_data['data'],
    )

    return web.json_response(
        status=202,
        data={
            'id': str(event.id),
        },
    )


async def delete_event_handler(request, *,
                               event_dispatcher_service: EventDispatcherService):
    """Handle events posting requests."""
    await event_dispatcher_service.dispatch_event_deletion(
        newsfeed_id=request.match_info['newsfeed_id'],
        event_id=request.match_info['event_id'],
    )
    return web.json_response(status=204)
