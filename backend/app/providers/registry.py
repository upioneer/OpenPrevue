"""Registry managing all active event ingestion providers."""

from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider
from backend.app.providers.mock import MockEventProvider


class ProviderRegistry:
    """Registry maintaining instances of configured event ingestion providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}
        # Register mock provider by default
        self.register(MockEventProvider())

    def register(self, provider: BaseProvider) -> None:
        """Register a provider instance."""
        self._providers[provider.provider_name] = provider
        logger.info("Registered event provider: %s", provider.provider_name)

    def get(self, name: str) -> BaseProvider | None:
        """Retrieve a registered provider by name."""
        return self._providers.get(name)

    def get_all(self) -> list[BaseProvider]:
        """Return all registered providers."""
        return list(self._providers.values())


provider_registry = ProviderRegistry()
