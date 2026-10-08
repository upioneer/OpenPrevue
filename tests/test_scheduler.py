"""Unit tests for background task scheduler."""

from zoneinfo import ZoneInfo

import pytest
from apscheduler.triggers.cron import CronTrigger
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


@pytest.mark.asyncio
async def test_midnight_rollover_job_registered_and_movable():
    """Verify the local-midnight sync job exists and follows timezone updates."""
    await init_db()

    await scheduler_mod.start_scheduler()
    try:
        assert scheduler_mod.scheduler.running is True
        job = scheduler_mod.scheduler.get_job(scheduler_mod.JOB_ID_MIDNIGHT_SYNC)
        assert job is not None
        assert isinstance(job.trigger, CronTrigger)
        assert job.next_run_time is not None
        assert (job.next_run_time.hour, job.next_run_time.minute) == (0, 5)

        scheduler_mod.reschedule_midnight_sync("America/Chicago")
        moved = scheduler_mod.scheduler.get_job(scheduler_mod.JOB_ID_MIDNIGHT_SYNC)
        assert str(moved.trigger.timezone) == str(ZoneInfo("America/Chicago"))

        scheduler_mod.reschedule_midnight_sync("Not/AZone")
        kept = scheduler_mod.scheduler.get_job(scheduler_mod.JOB_ID_MIDNIGHT_SYNC)
        assert str(kept.trigger.timezone) == str(ZoneInfo("America/Chicago"))
    finally:
        await scheduler_mod.shutdown_scheduler()
