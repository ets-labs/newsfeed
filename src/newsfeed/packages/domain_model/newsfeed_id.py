"""Newsfeed id module."""

from .error import DomainError


class NewsfeedIDSpecification:
    """Newsfeed id specification."""

    def __init__(self, max_length: int):
        """Initialize specification."""
        self.max_length = int(max_length)

    def is_satisfied_by(self, newsfeed_id: str) -> bool:
        """Check if subscription satisfies specification."""
        if not isinstance(newsfeed_id, str):
            raise NewsfeedIDTypeError(newsfeed_id)

        if len(newsfeed_id) > self.max_length:
            raise NewsfeedIDTooLongError(newsfeed_id, self.max_length)

        return True


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
