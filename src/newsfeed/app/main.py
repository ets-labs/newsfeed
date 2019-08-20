"""Main module."""

import os

from aiohttp import web

from .application import Application


def main():
    """Run application."""
    app = Application()
    web_app = app.create_web_app()
    web.run_app(web_app, port=int(os.getenv('PORT')))


if __name__ == '__main__':
    main()
