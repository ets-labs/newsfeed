"""Errors module."""


class DomainError(Exception):
    """Domain error."""

    @property
    def message(self) -> str:
        """Return error message."""
        return f'Domain error'
