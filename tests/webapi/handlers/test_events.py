"""Event handler tests."""

import uuid


async def test_get_events(web_client, app):
    """Check events posting handler."""
    newsfeed_id = '123'

    event_storage = app.infrastructure.event_storage()
    await event_storage.add(
        {
            'newsfeed_id': newsfeed_id,
            'data': {
                'event_data': 'some_data_1',
            },
        },
    )
    await event_storage.add(
        {
            'newsfeed_id': newsfeed_id,
            'data': {
                'event_data': 'some_data_2',
            },
        },
    )

    response = await web_client.get(f'/newsfeed/{newsfeed_id}/events/')

    assert response.status == 200
    data = await response.json()
    assert data == {
        'results': [
            {
                'newsfeed_id': newsfeed_id,
                'data': {
                    'event_data': 'some_data_2',
                },
            },
            {
                'newsfeed_id': newsfeed_id,
                'data': {
                    'event_data': 'some_data_1',
                },
            },
        ],
    }


async def test_post_events(web_client, app):
    """Check events posting handler."""
    newsfeed_id = '123'

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/events/',
        json={
            'data': {
                'event_data': 'some_data',
            },
        },
    )

    assert response.status == 202
    data = await response.json()
    assert uuid.UUID(data['id'])

    event_queue = app.infrastructure.event_queue()
    action, event_data = await event_queue.get()
    assert action == 'post'
    assert event_data['newsfeed_id'] == '123'
    assert event_data['data'] == {
        'event_data': 'some_data',
    }


async def test_post_event_with_abnormally_long_newsfeed_id(web_client, app):
    """Check events posting handler."""
    newsfeed_id_max_length = app.domain_model.newsfeed_id_specification().max_length
    newsfeed_id = 'x'*(newsfeed_id_max_length + 1)

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/events/',
        json={
            'data': {
                'event_data': 'some_data',
            },
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data['message'] == (
        f'Newsfeed id "{newsfeed_id[:newsfeed_id_max_length]}..." is too long'
    )

    event_queue = app.infrastructure.event_queue()
    assert await event_queue.is_empty()


async def test_delete_events(web_client, app):
    """Check events deletion handler."""
    newsfeed_id = '123'
    event_id = uuid.uuid4()

    response = await web_client.delete(f'/newsfeed/{newsfeed_id}/events/{event_id}/')

    assert response.status == 204

    event_queue = app.infrastructure.event_queue()
    action, event_data = await event_queue.get()
    assert action == 'delete'
    assert event_data['newsfeed_id'] == newsfeed_id
    assert event_data['event_id'] == str(event_id)
