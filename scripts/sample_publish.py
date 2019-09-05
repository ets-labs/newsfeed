"""Sample script for publishing to events."""

import sys
import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/events/',
                                json={
                                    'newsfeed_id': sys.argv[1],
                                    'data': {'payload': sys.argv[2]},
                                }) \
                as response:
            print(await response.json())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
