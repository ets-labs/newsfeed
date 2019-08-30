"""Miscellaneous handler tests."""


async def test_post_events(web_client, infrastructure):
    """Check events posting handler."""
    response = await web_client.post(
        '/events/',
        json={
            'newsfeed_id': '123',
            'data': {
                'event_data': 'some_data',
            },
        },
    )

    assert response.status == 202
    data = await response.json()
    assert data == {
        'id': '<new_event_id>',
    }

    event_queue = infrastructure.event_queue()
    event_data = await event_queue.get()
    assert event_data['newsfeed_id'] == '123'
    assert event_data['data'] == {
        'event_data': 'some_data',
    }


async def test_get_events(web_client, infrastructure):
    """Check events posting handler."""
    newsfeed_id = '123'

    event_storage = infrastructure.event_storage()
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

    response = await web_client.get(
        '/events/',
        params={
            'newsfeed_id': newsfeed_id,
        },
    )

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
