"""Script for integration testing of newsfeed service."""

import asyncio

import aiohttp


class ApiClient:
    """Service API client."""

    def __init__(self, url, session):
        """Initialize object."""
        self._base_url = url
        self._session = session

    def _url(self, uri):
        return f'{self._base_url}{uri}'

    async def get_events(self, newsfeed_id):
        """Get newsfeed events."""
        async with self._session.get(self._url(f'newsfeed/{newsfeed_id}/events/')) \
                as response:
            data = await response.json()
            return data['results']

    async def publish_event(self, newsfeed_id, event_data):
        """Publish event to newsfeed."""
        async with self._session.post(self._url(f'newsfeed/{newsfeed_id}/events/'),
                                      json={
                                          'data': event_data,
                                      }) \
                as response:
            return await response.json()

    async def delete_event(self, newsfeed_id, event_id):
        """Delete event from newsfeed."""
        async with self._session.delete(self._url(f'newsfeed/{newsfeed_id}/events/{event_id}/')) \
                as response:
            return response.status == 204

    async def get_subscriptions(self, newsfeed_id):
        """Get newsfeed subscriptions."""
        async with self._session.get(self._url(f'newsfeed/{newsfeed_id}/subscriptions/')) \
                as response:
            data = await response.json()
            return data['results']

    async def get_subscriber_subscriptions(self, newsfeed_id):
        """Get newsfeed subscriber subscriptions."""
        async with self._session.get(self._url(f'newsfeed/'
                                               f'{newsfeed_id}/subscribers/subscriptions/')) \
                as response:
            data = await response.json()
            return data['results']

    async def add_subscription(self, newsfeed_id, to_newsfeed_id):
        """Delete subscription to newsfeed."""
        async with self._session.post(self._url(f'newsfeed/{newsfeed_id}/subscriptions/'),
                                      json={
                                          'to_newsfeed_id': to_newsfeed_id,
                                      }) \
                as response:
            return await response.json()

    async def delete_subscription(self, newsfeed_id, subscription_id):
        """Delete subscription to newsfeed."""
        async with self._session.delete(self._url(f'newsfeed/{newsfeed_id}/subscriptions/'
                                                  f'{subscription_id}/')) \
                as response:
            return response.status == 204


class IntegrationTest1:
    """Integration test 1."""

    def __init__(self, api_client: ApiClient):
        """Initialize test."""
        self._api_client = api_client

    async def test(self):
        """Run test."""
        newsfeed_123 = '123'
        event_123_1 = await self._api_client.publish_event(
            newsfeed_id='123',
            event_data={
                'payload': 'event_1',
            },
        )

        event_123_1_deleted = await self._api_client.delete_event(
            newsfeed_id=newsfeed_123,
            event_id=event_123_1['id'],
        )
        assert event_123_1_deleted is True

        newsfeed_123_events = await self._api_client.get_events(newsfeed_id=newsfeed_123)
        assert len(newsfeed_123_events) == 0, newsfeed_123_events


class IntegrationTest2:
    """Integration test 2."""

    def __init__(self, api_client: ApiClient):
        """Initialize test."""
        self._api_client = api_client

    async def test(self):
        """Run test."""
        newsfeed_123 = '123'
        subscriber_124 = '124'
        subscriber_125 = '125'

        # Add subscriptions
        subscription_124_to_123, subscription_125_to_123 = await self._add_subscriptions(
            newsfeed_123=newsfeed_123,
            subscriber_124=subscriber_124,
            subscriber_125=subscriber_125,
        )

        # Add event
        event_123_1 = await self._publish_event(newsfeed_id=newsfeed_123)

        # Assert event publishing
        await self._assert_event_published_to_all_newsfeeds(
            event=event_123_1,
            newsfeed_123=newsfeed_123,
            subscriber_124=subscriber_124,
            subscriber_125=subscriber_125,
        )

        # Assert subscriptions
        await self._assert_123_subscriptions(
            newsfeed_123=newsfeed_123,
            subscription_125_to_123=subscription_125_to_123,
            subscription_124_to_123=subscription_124_to_123,
        )
        await self._assert_12x_subscriptions(
            subscriber_id=subscriber_124,
            subscription=subscription_124_to_123,
        )
        await self._assert_12x_subscriptions(
            subscriber_id=subscriber_125,
            subscription=subscription_125_to_123,
        )

        # Delete subscriptions
        await self._delete_subscriptions(subscription_125_to_123, subscription_124_to_123)

        # Assert that all subscriptions are deleted
        await self._assert_no_subscriber_subscriptions(newsfeed_123)
        await self._assert_no_subscriptions(subscriber_124, subscriber_125)

        # Delete events
        await self._delete_event(
            newsfeed_id=newsfeed_123,
            event=event_123_1,
        )

        # Assert that all events are deleted
        await self._assert_no_events(newsfeed_123, subscriber_124, subscriber_125)

    async def _add_subscriptions(self, newsfeed_123, subscriber_124, subscriber_125):
        subscription_124_to_123 = await self._api_client.add_subscription(
            newsfeed_id=subscriber_124,
            to_newsfeed_id=newsfeed_123,
        )
        subscription_125_to_123 = await self._api_client.add_subscription(
            newsfeed_id=subscriber_125,
            to_newsfeed_id=newsfeed_123,
        )
        return subscription_124_to_123, subscription_125_to_123

    async def _publish_event(self, newsfeed_id):
        return await self._api_client.publish_event(
            newsfeed_id=newsfeed_id,
            event_data={
                'payload': 'event_payload',
            },
        )

    async def _assert_event_published_to_all_newsfeeds(self, event, newsfeed_123,
                                                       subscriber_124, subscriber_125):
        newsfeed_123_events = await self._api_client.get_events(newsfeed_id=newsfeed_123)
        assert newsfeed_123_events[0]['id'] == event['id']
        assert newsfeed_123_events[0]['child_fqids'][0][0] == subscriber_125
        assert newsfeed_123_events[0]['child_fqids'][1][0] == subscriber_124

        newsfeed_125_events = await self._api_client.get_events(newsfeed_id=subscriber_125)
        assert newsfeed_125_events[0]['parent_fqid'] == [newsfeed_123, event['id']]
        assert newsfeed_125_events[0]['id'] == newsfeed_123_events[0]['child_fqids'][0][1]

        newsfeed_124_events = await self._api_client.get_events(newsfeed_id=subscriber_124)
        assert newsfeed_124_events[0]['parent_fqid'] == [newsfeed_123, event['id']]
        assert newsfeed_124_events[0]['id'] == newsfeed_123_events[0]['child_fqids'][1][1]

    async def _assert_123_subscriptions(self, newsfeed_123, subscription_125_to_123,
                                        subscription_124_to_123):
        newsfeed_123_subscriber_subscriptions = await self._api_client.get_subscriber_subscriptions(
            newsfeed_id=newsfeed_123,
        )
        assert newsfeed_123_subscriber_subscriptions[0]['id'] == subscription_125_to_123['id']
        assert newsfeed_123_subscriber_subscriptions[1]['id'] == subscription_124_to_123['id']

        newsfeed_123_subscriptions = await self._api_client.get_subscriptions(
            newsfeed_id=newsfeed_123,
        )
        assert len(newsfeed_123_subscriptions) == 0

    async def _assert_12x_subscriptions(self, subscriber_id, subscription):
        subscriber_subscriptions = await self._api_client.get_subscriber_subscriptions(
            newsfeed_id=subscriber_id,
        )
        assert len(subscriber_subscriptions) == 0

        subscriptions = await self._api_client.get_subscriptions(
            newsfeed_id=subscriber_id,
        )
        assert subscriptions[0]['id'] == subscription['id']

    async def _delete_subscriptions(self, *subscriptions):
        for subscription in subscriptions:
            await self._api_client.delete_subscription(
                newsfeed_id=subscription['newsfeed_id'],
                subscription_id=subscription['id'],
            )

    async def _assert_no_subscriptions(self, *newsfeed_ids):
        for newsfeed_id in newsfeed_ids:
            subscriptions = await self._api_client.get_subscriptions(newsfeed_id=newsfeed_id)
            assert len(subscriptions) == 0

    async def _assert_no_subscriber_subscriptions(self, *newsfeed_ids):
        for newsfeed_id in newsfeed_ids:
            subscriptions = await self._api_client.get_subscriber_subscriptions(
                newsfeed_id=newsfeed_id,
            )
            assert len(subscriptions) == 0

    async def _delete_event(self, newsfeed_id, event):
        event_123_1_deleted = await self._api_client.delete_event(
            newsfeed_id=newsfeed_id,
            event_id=event['id'],
        )
        assert event_123_1_deleted is True

    async def _assert_no_events(self, *newsfeed_ids):
        for newsfeed_id in newsfeed_ids:
            events = await self._api_client.get_events(newsfeed_id=newsfeed_id)
            assert len(events) == 0


async def main(url):
    """Run tests."""
    async with aiohttp.ClientSession() as session:
        api_client = ApiClient(url, session)

        test_1 = IntegrationTest1(api_client)
        await test_1.test()

        test_2 = IntegrationTest2(api_client)
        await test_2.test()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url='http://127.0.0.1:8000/api/'))
