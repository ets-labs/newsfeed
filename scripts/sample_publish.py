"""Sample script for posting events."""

import sys
import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        newsfeed_id = sys.argv[1]
        async with session.post(f'http://127.0.0.1:8000/newsfeed/{newsfeed_id}/events/',
                                json={
                                    'newsfeed_id': newsfeed_id,
                                    'data': {'payload': sys.argv[2]},
                                }) \
                as response:
            print(await response.json())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
