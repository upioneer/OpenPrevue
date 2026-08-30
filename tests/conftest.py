"""Pytest configuration and global fixtures for OpenPrevue test suite."""

import pytest
from backend.app.db.session import init_db
from backend.app.services.seeder import seed_initial_data


@pytest.fixture(autouse=True)
async def initialize_test_environment():
    """Ensure database schema is initialized and seeded for all test suites."""
    await init_db()
    await seed_initial_data()
