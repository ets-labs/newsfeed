"""Event API handlers."""

from typing import Dict, List, Tuple, Union, Any

from aiohttp import web
from dependency_injector.wiring import Provide

from newsfeed.domain.event import (
    Event,
    EventRepository,
)
from newsfeed.containers import Container
from newsfeed.domain.event_dispatcher import EventDispatcherService
from newsfeed.domain.error import DomainError


SerializedEventFQID = Tuple[str, str]
SerializedEvent = Dict[
    str,
    Union[
        str,
        int,
        Dict[Any, Any],
        SerializedEventFQID,
        List[SerializedEventFQID],
        None,
    ],
]


async def get_events_handler(
        request: web.Request, *,
        event_repository: EventRepository = Provide[Container.event_repository],
) -> web.Response:
    """Handle events getting requests."""
    newsfeed_id = request.match_info['newsfeed_id']

    newsfeed_events = await event_repository.get_by_newsfeed_id(newsfeed_id)

    return web.json_response(
        data={
            'results': [
                _serialize_event(event)
                for event in newsfeed_events
            ],
        },
    )


async def post_event_handler(
        request: web.Request, *,
        event_dispatcher_service: EventDispatcherService = Provide[Container.event_dispatcher_service],
) -> web.Response:
    """Handle events posting requests."""
    event_data = await request.json()

    try:
        event = await event_dispatcher_service.dispatch_new_event(
            newsfeed_id=request.match_info['newsfeed_id'],
            data=event_data['data'],
        )
    except DomainError as exception:
        return web.json_response(
            status=400,
            data={
                'message': exception.message,
            }
        )

    return web.json_response(
        status=202,
        data=_serialize_event(event),
    )


async def delete_event_handler(
        request: web.Request, *,
        event_dispatcher_service: EventDispatcherService = Provide[Container.event_dispatcher_service],
) -> web.Response:
    """Handle events posting requests."""
    await event_dispatcher_service.dispatch_event_deletion(
        newsfeed_id=request.match_info['newsfeed_id'],
        event_id=request.match_info['event_id'],
    )
    return web.json_response(status=204)


def _serialize_event(event: Event) -> SerializedEvent:
    return {
        'id': str(event.id),
        'newsfeed_id': str(event.newsfeed_id),
        'data': dict(event.data),
        'parent_fqid': (
            (event.parent_fqid.newsfeed_id, str(event.parent_fqid.event_id))
            if event.parent_fqid
            else None
        ),
        'child_fqids': [
            (child_fqid.newsfeed_id, str(child_fqid.event_id))
            for child_fqid in event.child_fqids
        ],
        'first_seen_at': int(event.first_seen_at.timestamp()),
        'published_at': int(event.published_at.timestamp()) if event.published_at else None,
    }
