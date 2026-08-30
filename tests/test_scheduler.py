"""Unit tests for background task scheduler."""

import pytest
from backend.app.services.scheduler import JOB_ID_SYNC, reschedule_sync_interval, scheduler, shutdown_scheduler, start_scheduler
from backend.app.db.session import init_db


@pytest.mark.asyncio
async def test_scheduler_lifecycle():
    """Verify scheduler startup, job registration, and reschedule."""
    await init_db()

    await start_scheduler()
    assert scheduler.running is True
    job = scheduler.get_job(JOB_ID_SYNC)
    assert job is not None

    # Test dynamic rescheduling
    reschedule_sync_interval(12)
    job_updated = scheduler.get_job(JOB_ID_SYNC)
    assert job_updated is not None

    await shutdown_scheduler()
