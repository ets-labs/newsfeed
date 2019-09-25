"""Event handlers."""

from aiohttp import web

from newsfeed.packages.domain_model.events import (
    EventDispatcherService,
    EventRepository,
)


async def post_event_handler(request, *,
                             event_dispatcher_service: EventDispatcherService):
    """Handle events posting requests."""
    newsfeed_id = request.match_info['newsfeed_id']
    data = await request.json()

    # TODO: fix that
    data['newsfeed_id'] = newsfeed_id

    event = await event_dispatcher_service.dispatch_event(event_data=data)

    return web.json_response(
        status=202,
        data={
            'id': str(event.id),
        },
    )


async def get_events_handler(request, *,
                             event_repository: EventRepository):
    """Handle events getting requests."""
    newsfeed_id = request.match_info['newsfeed_id']

    newsfeed_events = await event_repository.get_newsfeed(newsfeed_id)

    return web.json_response(
        data={
            'results': newsfeed_events,
        },
    )
