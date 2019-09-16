"""Sample script for testing posting of subscriptions and events."""

import aiohttp
import asyncio


async def publish_event(session, newsfeed_id, event_data):
    """Publish event to newsfeed."""
    async with session.post('http://127.0.0.1:8000/events/',
                            json={
                                'newsfeed_id': newsfeed_id,
                                'data': event_data,
                            }) \
            as response:
        print('Event posted -', await response.json())


async def subscribe(session, from_newsfeed_id, to_newsfeed_id):
    """Publish event to newsfeed."""
    async with session.post('http://127.0.0.1:8000/subscriptions/',
                            json={
                                'from_newsfeed_id': from_newsfeed_id,
                                'to_newsfeed_id': to_newsfeed_id,
                            }) \
            as response:
        print('Subscription posted -', await response.json())


async def main():
    async with aiohttp.ClientSession() as session:
        await publish_event(session, newsfeed_id='123', event_data={'payload': 'test_1'})

        await subscribe(session, from_newsfeed_id='124', to_newsfeed_id='123')
        await publish_event(session, newsfeed_id='123', event_data={'payload': 'test_2'})

        await subscribe(session, from_newsfeed_id='125', to_newsfeed_id='123')
        await publish_event(session, newsfeed_id='123', event_data={'payload': 'test_3'})


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
