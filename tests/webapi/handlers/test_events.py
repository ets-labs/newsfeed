"""Miscellaneous handler tests."""


async def test_post_events(web_client):
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
