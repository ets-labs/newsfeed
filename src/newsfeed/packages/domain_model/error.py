"""Errors module."""


class DomainError(Exception):
    """Domain error."""

    @property
    def message(self):
        """Return error message."""
        return f'Domain error'


class NewsfeedIDTypeError(DomainError):
    """Error indicating situations when newsfeed id has invalid type."""

    def __init__(self, newsfeed_id: str):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id

    @property
    def message(self):
        """Return error message."""
        return f'Newsfeed id "{self._newsfeed_id}" type is invalid'


class NewsfeedIDTooLongError(DomainError):
    """Error indicating situations when newsfeed id is too long."""

    def __init__(self, newsfeed_id: str, max_length: int):
        """Initialize error."""
        self._newsfeed_id = newsfeed_id
        self._max_length = max_length

    @property
    def message(self):
        """Return error message."""
        return f'Newsfeed id "{self._newsfeed_id[:self._max_length]}..." is too long'

