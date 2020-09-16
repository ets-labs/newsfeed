"""Event handler tests."""

import datetime
import uuid


async def test_get_events(web_client, container):
    """Check events posting handler."""
    newsfeed_id = '123'
    event_1 = {
        'id': str(uuid.uuid4()),
        'newsfeed_id': newsfeed_id,
        'data': {
            'event_data': 'some_data_1',
        },
        'parent_fqid': ['125', str(uuid.uuid4())],
        'child_fqids': [],
        'first_seen_at': datetime.datetime.utcnow().timestamp(),
        'published_at': None,
    }
    event_2 = {
        'id': str(uuid.uuid4()),
        'newsfeed_id': newsfeed_id,
        'data': {
            'event_data': 'some_data_2',
        },
        'parent_fqid': None,
        'child_fqids': [
            ['123', str(uuid.uuid4())],
            ['124', str(uuid.uuid4())],
        ],
        'first_seen_at': datetime.datetime.utcnow().timestamp(),
        'published_at': datetime.datetime.utcnow().timestamp(),
    }

    event_storage = container.event_storage()
    await event_storage.add(event_1)
    await event_storage.add(event_2)

    response = await web_client.get(f'/newsfeed/{newsfeed_id}/events/')

    assert response.status == 200
    data = await response.json()
    assert data == {
        'results': [
            {
                'id': event_2['id'],
                'newsfeed_id': newsfeed_id,
                'data': event_2['data'],
                'parent_fqid': event_2['parent_fqid'],
                'child_fqids': event_2['child_fqids'],
                'first_seen_at': int(event_2['first_seen_at']),
                'published_at': int(event_2['published_at']),
            },
            {
                'id': event_1['id'],
                'newsfeed_id': newsfeed_id,
                'data': event_1['data'],
                'parent_fqid': event_1['parent_fqid'],
                'child_fqids': event_1['child_fqids'],
                'first_seen_at': int(event_1['first_seen_at']),
                'published_at': event_1['published_at'],
            },
        ],
    }


async def test_post_events(web_client, container):
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

    event_queue = container.event_queue()
    action, event_data = await event_queue.get()
    assert action == 'post'
    assert event_data['newsfeed_id'] == '123'
    assert event_data['data'] == {
        'event_data': 'some_data',
    }


async def test_post_event_with_abnormally_long_newsfeed_id(web_client, container):
    """Check events posting handler."""
    newsfeed_id_max_length = container.newsfeed_id_specification().max_length
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

    event_queue = container.event_queue()
    assert await event_queue.is_empty()


async def test_delete_events(web_client, container):
    """Check events deletion handler."""
    newsfeed_id = '123'
    event_id = uuid.uuid4()

    response = await web_client.delete(f'/newsfeed/{newsfeed_id}/events/{event_id}/')

    assert response.status == 204

    event_queue = container.event_queue()
    action, event_data = await event_queue.get()
    assert action == 'delete'
    assert event_data['newsfeed_id'] == newsfeed_id
    assert event_data['event_id'] == str(event_id)
