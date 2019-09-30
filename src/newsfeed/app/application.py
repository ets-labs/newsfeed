"""Application module."""

from .containers import Infrastructure, DomainModel, WebApi


class Application:
    """Application."""

    def __init__(self, infrastructure: Infrastructure, domain_model: DomainModel, web_api: WebApi):
        """Initialize application."""
        self.infrastructure = infrastructure

        self.domain_model = domain_model
        self.domain_model.infra.override(self.infrastructure)

        self.web_api = web_api
        self.web_api.domain.override(self.domain_model)
