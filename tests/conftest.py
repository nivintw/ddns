# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Shared pytest fixtures for the digital_ocean_dynamic_dns test suite."""

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
import pytest_mock
import responses

from digital_ocean_dynamic_dns import domains, ip, manage, subdomains
from digital_ocean_dynamic_dns.database import connect_database


@pytest.fixture
def mocked_responses() -> Generator[responses.RequestsMock, None, None]:
    """Provide a responses.RequestsMock context for intercepting HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def temp_database_path(tmp_path: Path) -> Path:
    """Return a temporary path for a test-specific SQLite database file."""
    db_root = tmp_path
    return db_root / "ddns.db"


@pytest.fixture(autouse=True)
def mock_db_for_test(
    temp_database_path: Path,
    mocker: pytest_mock.MockerFixture,
) -> sqlite3.Connection:
    """Mock connection object to have a per-test connection / database.

    Ensures isolation of the database state between tests.

    In this module we have to mock out the conn objects everywhere they are created
      in order to ensure all modules/functions are using the same databases.

    """
    test_specific_conn = connect_database(temp_database_path)
    mocker.patch.object(domains, "conn", test_specific_conn)
    mocker.patch.object(subdomains, "conn", test_specific_conn)
    mocker.patch.object(ip, "conn", test_specific_conn)
    mocker.patch.object(manage, "conn", test_specific_conn)

    return test_specific_conn


@pytest.fixture
def preload_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    """Load a sentinel API key.

    Almost all operations require an api key to be configured.
    This fixture provides a sentinel / not-real API key for us to use.

    This fixture sets the API token in _both_ places:
    1. Env var DIGITALOCEAN_TOKEN.
    2. The database table.

    In theory, setting this API token in the database should be redundant
      with setting DIGITALOCEAN_TOKEN, however, no strong reason to not set both.
    """
    sentinel_api_key = "sentinel-api-key"  # pragma: allowlist secret
    monkeypatch.setenv("DIGITALOCEAN_TOKEN", sentinel_api_key)
    return sentinel_api_key


@pytest.fixture(autouse=True)
def clear_local_env_var_for_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure that the tests aren't infected by local env vars."""
    monkeypatch.delenv("DIGITALOCEAN_TOKEN", raising=False)
