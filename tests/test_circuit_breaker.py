"""Unit tests for provider circuit breaker state machine."""

from datetime import datetime, timedelta, timezone
import pytest
from backend.app.core.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_initial_state():
    """Verify breaker begins in CLOSED operational state."""
    breaker = CircuitBreaker(name="test_provider", failure_threshold=3)
    assert breaker.state == CircuitState.CLOSED
    assert breaker.can_execute() is True


def test_circuit_breaker_trips_on_failures():
    """Verify breaker trips to OPEN after reaching threshold."""
    breaker = CircuitBreaker(name="test_provider", failure_threshold=3, recovery_timeout_seconds=60)
    breaker.record_failure("HTTP 500")
    assert breaker.state == CircuitState.CLOSED
    assert breaker.can_execute() is True

    breaker.record_failure("HTTP 502")
    assert breaker.state == CircuitState.CLOSED

    breaker.record_failure("HTTP 503")
    assert breaker.state == CircuitState.OPEN
    assert breaker.can_execute() is False


def test_circuit_breaker_recovery_half_open():
    """Verify breaker transitions to HALF_OPEN probe after timeout."""
    breaker = CircuitBreaker(name="test_provider", failure_threshold=2, recovery_timeout_seconds=10)
    breaker.record_failure("Error 1")
    breaker.record_failure("Error 2")
    assert breaker.state == CircuitState.OPEN

    # Simulate elapsed time
    breaker.last_state_change = datetime.now(timezone.utc) - timedelta(seconds=15)
    assert breaker.can_execute() is True
    assert breaker.state == CircuitState.HALF_OPEN

    # Success closes circuit
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


def test_circuit_breaker_probe_failure_backs_off():
    """Verify failed canary probe in HALF_OPEN doubles timeout and re-opens."""
    breaker = CircuitBreaker(name="test_provider", failure_threshold=2, recovery_timeout_seconds=10)
    breaker.record_failure("Error 1")
    breaker.record_failure("Error 2")
    assert breaker.state == CircuitState.OPEN

    # Transition to half-open
    breaker.last_state_change = datetime.now(timezone.utc) - timedelta(seconds=15)
    breaker.can_execute()
    assert breaker.state == CircuitState.HALF_OPEN

    # Probe fails
    breaker.record_failure("Canary Timeout")
    assert breaker.state == CircuitState.OPEN
    assert breaker.current_recovery_timeout == 20.0
