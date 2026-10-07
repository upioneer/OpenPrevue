"""Pytest configuration and global fixtures for OpenPrevue test suite."""

import os
import tempfile

# Isolate the suite from the developer/live database. Settings bind DATA_DIR
# at import time, so this must run before any backend module is imported.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="openprevue-pytest-")

import pytest
from backend.app.db.session import init_db
from backend.app.services.seeder import seed_initial_data


@pytest.fixture(autouse=True)
async def initialize_test_environment():
    """Ensure database schema is initialized and seeded for all test suites."""
    await init_db()
    await seed_initial_data()
