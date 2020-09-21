"""Errors module."""


class DomainError(Exception):

    @property
    def message(self) -> str:
        return 'Domain error'
