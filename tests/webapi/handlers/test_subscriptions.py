"""Subscription handler tests."""

import uuid
import datetime


async def test_get_subscriptions(web_client, app):
    """Check subscriptions getting handler."""
    newsfeed_id = '123'

    subscription_storage = app.infrastructure.subscription_storage()
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': newsfeed_id,
            'to_newsfeed_id': '124',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': newsfeed_id,
            'to_newsfeed_id': '125',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': '125',
            'to_newsfeed_id': '126',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )

    response = await web_client.get(f'/newsfeed/{newsfeed_id}/subscriptions/')

    assert response.status == 200
    data = await response.json()
    subscription_1, subscription_2 = data['results']

    assert uuid.UUID(subscription_1['id'])
    assert subscription_1['newsfeed_id'] == newsfeed_id
    assert subscription_1['to_newsfeed_id'] == '125'
    assert int(subscription_1['subscribed_at'])

    assert uuid.UUID(subscription_2['id'])
    assert subscription_2['newsfeed_id'] == newsfeed_id
    assert subscription_2['to_newsfeed_id'] == '124'
    assert int(subscription_2['subscribed_at'])


async def test_post_subscriptions(web_client, app):
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

    subscription_storage = app.infrastructure.subscription_storage()
    subscriptions = await subscription_storage.get_by_to_newsfeed_id(newsfeed_id='123')
    assert len(subscriptions) == 1
    assert subscriptions[0]['newsfeed_id'] == '124'
    assert subscriptions[0]['to_newsfeed_id'] == '123'


async def test_post_subscription_to_self(web_client, app):
    """Check subscriptions posting handler."""
    newsfeed_id = '124'

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/subscriptions/',
        json={
            'to_newsfeed_id': newsfeed_id,
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data['message'] == f'Subscription of newsfeed "{newsfeed_id}" to itself is restricted'

    subscription_storage = app.infrastructure.subscription_storage()
    subscriptions = await subscription_storage.get_by_newsfeed_id(newsfeed_id=newsfeed_id)
    assert len(subscriptions) == 0


async def test_post_subscription_with_abnormally_long_newsfeed_id(web_client, app):
    """Check subscriptions posting handler."""
    newsfeed_id_max_length = app.domain_model.newsfeed_id_specification().max_length
    newsfeed_id = 'x'*(newsfeed_id_max_length + 1)

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/subscriptions/',
        json={
            'to_newsfeed_id': newsfeed_id,
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data['message'] == (
        f'Newsfeed id "{newsfeed_id[:newsfeed_id_max_length]}..." is too long'
    )

    subscription_storage = app.infrastructure.subscription_storage()
    subscriptions = await subscription_storage.get_by_newsfeed_id(newsfeed_id=newsfeed_id)
    assert len(subscriptions) == 0


async def test_post_subscription_with_abnormally_long_to_newsfeed_id(web_client, app):
    """Check subscriptions posting handler."""
    newsfeed_id = '124'

    newsfeed_id_max_length = app.domain_model.newsfeed_id_specification().max_length
    to_newsfeed_id = 'x'*(newsfeed_id_max_length + 1)

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/subscriptions/',
        json={
            'to_newsfeed_id': to_newsfeed_id,
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data['message'] == (
        f'Newsfeed id "{to_newsfeed_id[:newsfeed_id_max_length]}..." is too long'
    )

    subscription_storage = app.infrastructure.subscription_storage()
    subscriptions = await subscription_storage.get_by_newsfeed_id(newsfeed_id=newsfeed_id)
    assert len(subscriptions) == 0


async def test_post_multiple_subscriptions_to_the_same_feed(web_client, app):
    """Check subscriptions posting handler."""
    newsfeed_id = '123'
    to_newsfeed_id = '124'

    subscription_storage = app.infrastructure.subscription_storage()
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': newsfeed_id,
            'to_newsfeed_id': to_newsfeed_id,
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )

    response = await web_client.post(
        f'/newsfeed/{newsfeed_id}/subscriptions/',
        json={
            'to_newsfeed_id': to_newsfeed_id,
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data['message'] == (
        f'Subscription from newsfeed "{newsfeed_id}" to "{to_newsfeed_id}" already exists'
    )

    subscription_storage = app.infrastructure.subscription_storage()
    subscriptions = await subscription_storage.get_by_to_newsfeed_id(newsfeed_id=to_newsfeed_id)
    assert len(subscriptions) == 1
    assert subscriptions[0]['newsfeed_id'] == newsfeed_id
    assert subscriptions[0]['to_newsfeed_id'] == to_newsfeed_id


async def test_delete_subscriptions(web_client, app):
    """Check subscriptions deleting handler."""
    newsfeed_id = '123'

    subscription_id_1 = uuid.uuid4()
    subscription_id_2 = uuid.uuid4()
    subscription_id_3 = uuid.uuid4()

    subscription_storage = app.infrastructure.subscription_storage()
    await subscription_storage.add(
        {
            'id': str(subscription_id_1),
            'newsfeed_id': newsfeed_id,
            'to_newsfeed_id': '124',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(subscription_id_2),
            'newsfeed_id': newsfeed_id,
            'to_newsfeed_id': '125',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(subscription_id_3),
            'newsfeed_id': '125',
            'to_newsfeed_id': '126',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )

    response = await web_client.delete(
        f'/newsfeed/{newsfeed_id}/subscriptions/{subscription_id_1}/',
    )

    assert response.status == 204

    subscription_2, = await subscription_storage.get_by_newsfeed_id(newsfeed_id)
    assert uuid.UUID(subscription_2['id']) == subscription_id_2

    assert len(await subscription_storage.get_by_to_newsfeed_id('124')) == 0
    assert len(await subscription_storage.get_by_to_newsfeed_id('125')) == 1
    assert len(await subscription_storage.get_by_to_newsfeed_id('126')) == 1


async def test_get_subscriber_subscriptions(web_client, app):
    """Check subscriber subscriptions getting handler."""
    newsfeed_id = '123'

    subscription_storage = app.infrastructure.subscription_storage()
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': '124',
            'to_newsfeed_id': newsfeed_id,
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': '125',
            'to_newsfeed_id': newsfeed_id,
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )
    await subscription_storage.add(
        {
            'id': str(uuid.uuid4()),
            'newsfeed_id': '125',
            'to_newsfeed_id': '126',
            'subscribed_at': datetime.datetime.utcnow().timestamp(),
        },
    )

    response = await web_client.get(f'/newsfeed/{newsfeed_id}/subscribers/subscriptions/')

    assert response.status == 200
    data = await response.json()
    subscription_1, subscription_2 = data['results']

    assert uuid.UUID(subscription_1['id'])
    assert subscription_1['newsfeed_id'] == '125'
    assert subscription_1['to_newsfeed_id'] == newsfeed_id
    assert int(subscription_1['subscribed_at'])

    assert uuid.UUID(subscription_2['id'])
    assert subscription_2['newsfeed_id'] == '124'
    assert subscription_2['to_newsfeed_id'] == newsfeed_id
    assert int(subscription_2['subscribed_at'])
