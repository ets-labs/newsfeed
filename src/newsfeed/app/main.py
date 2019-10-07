"""Main module."""

from .factory import application_factory


if __name__ == '__main__':
    application = application_factory()
    application.main()
