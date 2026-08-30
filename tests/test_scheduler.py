"""Unit tests for background task scheduler."""

import pytest
from backend.app.services import scheduler as scheduler_mod
from backend.app.db.session import init_db


@pytest.mark.asyncio
async def test_scheduler_lifecycle():
    """Verify scheduler startup, job registration, and reschedule."""
    await init_db()

    await scheduler_mod.start_scheduler()
    assert scheduler_mod.scheduler.running is True
    job = scheduler_mod.scheduler.get_job(scheduler_mod.JOB_ID_SYNC)
    assert job is not None

    # Test dynamic rescheduling
    scheduler_mod.reschedule_sync_interval(12)
    job_updated = scheduler_mod.scheduler.get_job(scheduler_mod.JOB_ID_SYNC)
    assert job_updated is not None

    await scheduler_mod.shutdown_scheduler()
