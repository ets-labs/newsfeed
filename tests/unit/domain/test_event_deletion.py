"""Event deletion tests."""


async def test_event_deletion(container):
    """Check event deletion."""
    newsfeed_id = '123'

    event_dispatcher_service = container.event_dispatcher_service()
    event_processor_service = container.event_processor_service()

    event_1 = await _process_new_event(
        event_dispatcher_service,
        event_processor_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_1',
        },
    )
    event_2 = await _process_new_event(
        event_dispatcher_service,
        event_processor_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_2',
        },
    )

    await _process_event_deletion(
        event_dispatcher_service,
        event_processor_service,
        newsfeed_id=newsfeed_id,
        event_id=event_1.id,
    )

    event_repository = container.event_repository()
    events = await event_repository.get_by_newsfeed_id(newsfeed_id)
    assert len(events) == 1
    assert events[0].id == event_2.id
    assert events[0].data == event_2.data


async def test_event_deletion_from_subscriber(container):
    """Check event deletion."""
    newsfeed_id = '123'
    subscriber_newsfeed_id = '124'

    subscription_service = container.subscription_service()
    await subscription_service.create_subscription(
        newsfeed_id=subscriber_newsfeed_id,
        to_newsfeed_id=newsfeed_id,
    )

    event_dispatcher_service = container.event_dispatcher_service()
    event_processor_service = container.event_processor_service()

    event_1 = await _process_new_event(
        event_dispatcher_service,
        event_processor_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_1',
        },
    )
    event_2 = await _process_new_event(
        event_dispatcher_service,
        event_processor_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_2',
        },
    )

    await _process_event_deletion(
        event_dispatcher_service,
        event_processor_service,
        newsfeed_id=newsfeed_id,
        event_id=event_1.id,
    )

    event_repository = container.event_repository()
    events = await event_repository.get_by_newsfeed_id(newsfeed_id)
    assert len(events) == 1
    assert events[0].id == event_2.id
    assert events[0].newsfeed_id == event_2.newsfeed_id
    assert events[0].data == event_2.data

    subscriber_events = await event_repository.get_by_newsfeed_id(subscriber_newsfeed_id)
    assert len(subscriber_events) == 1
    assert subscriber_events[0].parent_fqid.newsfeed_id == event_2.newsfeed_id
    assert subscriber_events[0].parent_fqid.event_id == event_2.id
    assert subscriber_events[0].data == event_2.data


async def _process_new_event(event_dispatcher_service, event_processor_service, newsfeed_id, data):
    event = await event_dispatcher_service.dispatch_new_event(
        newsfeed_id=newsfeed_id,
        data=data,
    )
    await event_processor_service.process_event()
    return event


async def _process_event_deletion(event_dispatcher_service, event_processor_service, newsfeed_id,
                                  event_id):
    await event_dispatcher_service.dispatch_event_deletion(
        newsfeed_id=newsfeed_id,
        event_id=str(event_id),
    )
    await event_processor_service.process_event()
