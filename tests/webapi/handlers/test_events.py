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
