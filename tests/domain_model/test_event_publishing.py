"""Event publishing tests."""

from pytest import fixture


async def test_event_publishing(domain_model):
    """Check event publishing."""
    newsfeed_id = '123'

    event_dispatcher_service = domain_model.event_dispatcher_service()
    event_publisher_service = domain_model.event_publisher_service()

    await _process_event(
        event_dispatcher_service,
        event_publisher_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_1',
        },
    )
    await _process_event(
        event_dispatcher_service,
        event_publisher_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_2',
        },
    )

    event_repository = domain_model.event_repository()
    events = await event_repository.get_newsfeed(newsfeed_id)
    assert events[0]['data'] == {
        'event_data': 'some_data_2',
    }
    assert events[1]['data'] == {
        'event_data': 'some_data_1',
    }


async def test_event_publishing_to_subscriber(domain_model):
    """Check event publishing."""
    newsfeed_id = '123'
    subscriber_newsfeed_id = '124'

    subscription_service = domain_model.subscription_service()
    await subscription_service.create_subscription(
        {
            'from_newsfeed_id': subscriber_newsfeed_id,
            'to_newsfeed_id': newsfeed_id,
        },
    )

    event_dispatcher_service = domain_model.event_dispatcher_service()
    event_publisher_service = domain_model.event_publisher_service()

    await _process_event(
        event_dispatcher_service,
        event_publisher_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_1',
        },
    )
    await _process_event(
        event_dispatcher_service,
        event_publisher_service,
        newsfeed_id=newsfeed_id,
        data={
            'event_data': 'some_data_2',
        },
    )

    event_repository = domain_model.event_repository()
    events = await event_repository.get_newsfeed(newsfeed_id)
    assert events[0]['data'] == {
        'event_data': 'some_data_2',
    }
    assert events[1]['data'] == {
        'event_data': 'some_data_1',
    }

    subscriber_events = await event_repository.get_newsfeed(subscriber_newsfeed_id)
    assert subscriber_events[0]['data'] == {
        'event_data': 'some_data_2',
    }
    assert subscriber_events[1]['data'] == {
        'event_data': 'some_data_1',
    }


async def _process_event(event_dispatcher_service, event_publisher_service, newsfeed_id, data):
    await event_dispatcher_service.dispatch_event(
        event_data={
            'newsfeed_id': newsfeed_id,
            'data': data,
        },
    )
    await event_publisher_service.process_event()
