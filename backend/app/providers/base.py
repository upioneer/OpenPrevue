"""Abstract base provider interface for event ingestion sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel


@dataclass
class GeoPoint:
    """Geographic coordinate representation."""
    latitude: float
    longitude: float


class RateLimitConfig(BaseModel):
    """Rate limit configuration for an external provider."""
    requests_per_minute: int = 60
    max_retries: int = 3
    retry_delay_seconds: float = 2.0


class RawEvent(BaseModel):
    """Normalized intermediate event representation emitted by providers."""
    source: str
    source_event_id: str
    venue_name: str
    venue_address: str | None = None
    venue_city: str | None = None
    venue_state: str | None = None
    venue_postal_code: str | None = None
    venue_latitude: float | None = None
    venue_longitude: float | None = None
    title: str
    description: str | None = None
    category: str = "other"
    start_time: str
    end_time: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    currency: str = "USD"
    image_url: str | None = None
    ticket_url: str
    is_featured: int = 0


@dataclass
class ProviderStatus:
    """Current reachability and status of a provider."""
    provider_name: str
    status: str
    is_healthy: bool
    last_sync: datetime | None = None
    cached_events_count: int = 0
    error_message: str | None = None
    extra_details: dict = field(default_factory=dict)


class BaseProvider(ABC):
    """Abstract base class that all event ingestion adapters must implement."""

    provider_name: str
    rate_limit: RateLimitConfig = RateLimitConfig()

    @abstractmethod
    async def fetch_events(self, location: GeoPoint, radius_miles: float) -> list[RawEvent]:
        """Fetch raw events from the provider within the specified geographical boundary."""
        pass

    async def healthcheck(self) -> ProviderStatus:
        """Return the current reachability and quota status of the provider."""
        return ProviderStatus(
            provider_name=self.provider_name,
            status="ok",
            is_healthy=True,
        )
