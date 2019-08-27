"""Event publishing tests."""


async def test_event_publishing(domain_model):
    """Check event publishing."""
    newsfeed_id = '123'

    event_dispatcher_service = domain_model.event_dispatcher_service()
    await event_dispatcher_service.dispatch_event(
        event_data={
            'newsfeed_id': newsfeed_id,
            'data': {
                'event_data': 'some_data_1',
            },
        },
    )
    await event_dispatcher_service.dispatch_event(
        event_data={
            'newsfeed_id': newsfeed_id,
            'data': {
                'event_data': 'some_data_2',
            },
        },
    )

    event_publisher_service = domain_model.event_publisher_service()
    await event_publisher_service.process_event()
    await event_publisher_service.process_event()

    event_repository = domain_model.event_repository()
    events = await event_repository.get_newsfeed(newsfeed_id)
    assert events[0]['data'] == {
        'event_data': 'some_data_2',
    }
    assert events[1]['data'] == {
        'event_data': 'some_data_1',
    }
