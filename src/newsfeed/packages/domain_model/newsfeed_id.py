"""Newsfeed id module."""

from .error import (
    NewsfeedIDTypeError,
    NewsfeedIDTooLongError,
)


class NewsfeedIDSpecification:
    """Newsfeed id specification."""

    def __init__(self, max_length):
        """Initialize specification."""
        self.max_length = max_length

    def is_satisfied_by(self, newsfeed_id: str) -> bool:
        """Check if subscription satisfies specification."""
        if not isinstance(newsfeed_id, str):
            raise NewsfeedIDTypeError(newsfeed_id)

        if len(newsfeed_id) > self.max_length:
            raise NewsfeedIDTooLongError(newsfeed_id, self.max_length)

        return True
