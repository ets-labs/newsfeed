"""Main module."""

import os

from aiohttp import web

from .app import create_app


if __name__ == '__main__':
    app = create_app()
    web.run_app(
        app,
        port=int(os.getenv('PORT', 8000)),
    )
