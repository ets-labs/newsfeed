"""Application module."""

from .containers import DomainModel, WebApi


class Application:
    """Application."""

    def create_web_app(self):
        """Create web application."""
        domain_model, web_api = self.create_containers()

        web_app = web_api.web_app()
        web_app.domain_model = domain_model
        web_app.web_api = web_api

        return web_app

    def create_containers(self):
        """Create application containers."""
        domain_model = DomainModel()
        web_api = WebApi(domain=domain_model)

        return domain_model, web_api
