"""Subscription handler tests."""

import uuid
import datetime


async def test_post_subscriptions(web_client, infrastructure):
    """Check subscriptions posting handler."""
    newsfeed_id = '124'

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/subscriptions/',
        json={
            'to_newsfeed_id': '123',
        },
    )

    assert response.status == 200
    data = await response.json()
    assert uuid.UUID(data['id'])

    subscription_storage = infrastructure.subscription_storage()
    subscriptions = await subscription_storage.get_to(newsfeed_id='123')
    assert len(subscriptions) == 1
    assert subscriptions[0]['from_newsfeed_id'] == '124'
    assert subscriptions[0]['to_newsfeed_id'] == '123'


async def test_get_subscriptions(web_client, infrastructure):
    """Check subscriptions getting handler."""
    newsfeed_id = '123'

    subscription_storage = infrastructure.subscription_storage()
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'from_newsfeed_id': newsfeed_id,
            'to_newsfeed_id': '124',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'from_newsfeed_id': newsfeed_id,
            'to_newsfeed_id': '125',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'from_newsfeed_id': '125',
            'to_newsfeed_id': '126',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )

    response = await web_client.get(f'/newsfeed/{newsfeed_id}/subscriptions/')

    assert response.status == 200
    data = await response.json()
    subscription_1, subscription_2 = data['results']

    assert uuid.UUID(subscription_1['id'])
    assert subscription_1['from_newsfeed_id'] == newsfeed_id
    assert subscription_1['to_newsfeed_id'] == '125'
    assert int(subscription_1['subscribed_at'])

    assert uuid.UUID(subscription_2['id'])
    assert subscription_2['from_newsfeed_id'] == newsfeed_id
    assert subscription_2['to_newsfeed_id'] == '124'
    assert int(subscription_2['subscribed_at'])
