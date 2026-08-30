"""Registry managing all active and configured event ingestion providers."""

from backend.app.core.logging import logger
from backend.app.providers.base import BaseProvider
from backend.app.providers.eventbrite import EventbriteProvider
from backend.app.providers.ical import ICalEventProvider
from backend.app.providers.json_ld import JsonLdEventProvider
from backend.app.providers.mock import MockEventProvider
from backend.app.providers.seatgeek import SeatGeekProvider
from backend.app.providers.ticketmaster import TicketmasterProvider


class ProviderRegistry:
    """Registry maintaining instances of configured event ingestion providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}
        self._init_default_providers()

    def _init_default_providers(self) -> None:
        """Initialize and register all supported provider adapters."""
        self.register(MockEventProvider())
        self.register(TicketmasterProvider())
        self.register(SeatGeekProvider())
        self.register(EventbriteProvider())
        self.register(JsonLdEventProvider())
        self.register(ICalEventProvider())

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
