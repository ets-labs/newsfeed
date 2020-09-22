"""Miscellaneous handler tests."""


async def test_status(web_client):
    """Check status handler."""
    response = await web_client.get('/status/')

    assert response.status == 200
    data = await response.json()
    assert data == {'status': 'OK'}
