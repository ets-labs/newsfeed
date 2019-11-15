"""Application main module."""

from .application import Application
from .configuration import get_config

if __name__ == '__main__':
    application = Application(config=get_config())
    application.main()
