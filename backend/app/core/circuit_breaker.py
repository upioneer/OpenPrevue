"""Circuit breaker state machine for external provider fault isolation."""

from datetime import datetime, timezone
from enum import Enum
from backend.app.core.logging import logger


class CircuitState(str, Enum):
    """Circuit breaker lifecycle states."""
    CLOSED = "closed"        # Normal operational state, requests pass through
    OPEN = "open"            # Tripped state, calls are immediately failed/skipped
    HALF_OPEN = "half_open"  # Probing state, single canary request allowed


class CircuitBreaker:
    """Isolates failing external providers to prevent resource exhaustion."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 900.0,  # 15 minutes default
        max_recovery_timeout_seconds: float = 7200.0,  # 2 hours max
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.base_recovery_timeout = recovery_timeout_seconds
        self.current_recovery_timeout = recovery_timeout_seconds
        self.max_recovery_timeout = max_recovery_timeout_seconds

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: datetime | None = None
        self.last_state_change: datetime = datetime.now(timezone.utc)
        self.last_error: str | None = None

    def can_execute(self) -> bool:
        """Evaluate if an outbound request is permitted under current circuit state."""
        now = datetime.now(timezone.utc)

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timer has elapsed to enter half-open probe state
            elapsed = (now - self.last_state_change).total_seconds()
            if elapsed >= self.current_recovery_timeout:
                logger.info(
                    "Circuit breaker [%s] recovery timer (%.0fs) expired. Transitioning from OPEN to HALF_OPEN probe.",
                    self.name,
                    self.current_recovery_timeout,
                )
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow canary request
            return True

        return False

    def record_success(self) -> None:
        """Record a successful provider request."""
        now = datetime.now(timezone.utc)
        if self.state in (CircuitState.HALF_OPEN, CircuitState.OPEN):
            logger.info("Circuit breaker [%s] probe succeeded. Transitioning to CLOSED.", self.name)
            self.state = CircuitState.CLOSED
            self.last_state_change = now
            self.current_recovery_timeout = self.base_recovery_timeout

        self.failure_count = 0
        self.last_error = None

    def record_failure(self, error: Exception | str) -> None:
        """Record a failed provider request and trip circuit if threshold exceeded."""
        now = datetime.now(timezone.utc)
        self.failure_count += 1
        self.last_failure_time = now
        self.last_error = str(error)

        if self.state == CircuitState.HALF_OPEN:
            # Probe failed, back off with doubled recovery timeout
            self.current_recovery_timeout = min(
                self.current_recovery_timeout * 2,
                self.max_recovery_timeout,
            )
            self.state = CircuitState.OPEN
            self.last_state_change = now
            logger.warning(
                "Circuit breaker [%s] canary probe failed: %s. Re-opening circuit with %.0fs timeout.",
                self.name,
                self.last_error,
                self.current_recovery_timeout,
            )

        elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = now
            logger.warning(
                "Circuit breaker [%s] exceeded %d failures (%s). Tripping to OPEN state for %.0fs.",
                self.name,
                self.failure_threshold,
                self.last_error,
                self.current_recovery_timeout,
            )


class CircuitBreakerRegistry:
    """Registry maintaining circuit breakers per provider."""

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}

    def get_breaker(self, name: str) -> CircuitBreaker:
        """Retrieve or create a circuit breaker for a provider."""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name=name)
        return self._breakers[name]


circuit_registry = CircuitBreakerRegistry()
