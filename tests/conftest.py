# digital-ocean-dynamic-dns
# Copyright (C) 2023 Tyler Nivin <tyler@nivin.tech>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software
#   without restriction, including without limitation the rights to use, copy, modify, merge,
#   publish, distribute, sublicense, and/or sell copies of the Software,
#   and to permit persons to whom the Software is furnished to do so,
#   subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#   OR OTHER DEALINGS IN THE SOFTWARE.
#
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the digital-ocean-dynamic-dns contributors

from pathlib import Path
from sqlite3 import Connection

import pytest
import responses

from digital_ocean_dynamic_dns import api_key_helpers, domains, ip, manage, subdomains
from digital_ocean_dynamic_dns.database import connect_database


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def temp_database_path(tmp_path: Path) -> Path:
    db_root = tmp_path
    return db_root / "ddns.db"


@pytest.fixture()
def mock_db_for_test(temp_database_path: Path, mocker):
    """Mock connection object to have a per-test connection / database.
    Ensures isolation of the database state between tests.

    In this module we have to mock out the conn objects everywhere they are created
      in order to ensure all modules/functions are using the same databases.

    """
    test_specific_conn = connect_database(temp_database_path)
    mocker.patch.object(domains, "conn", test_specific_conn)
    mocker.patch.object(api_key_helpers, "conn", test_specific_conn)
    mocker.patch.object(subdomains, "conn", test_specific_conn)
    mocker.patch.object(ip, "conn", test_specific_conn)
    mocker.patch.object(manage, "conn", test_specific_conn)

    return test_specific_conn


@pytest.fixture()
def preload_api_key(
    mock_db_for_test: Connection,
    monkeypatch: pytest.MonkeyPatch,
):
    """Load a sentinel API key.
    Almost all operations require an api key to be configured.
    This fixture provides a sentinel / not-real API key for us to use.

    This fixture sets the API token in _both_ places:
    1. Env var DIGITALOCEAN_TOKEN.
    2. The database table.

    In theory, setting this API token in the database should be redundant
      with setting DIGITALOCEAN_TOKEN, however, no strong reason to not set both.
    """
    SENTINEL_API_KEY = "sentinel-api-key"  # pragma: allowlist secret
    monkeypatch.setenv("DIGITALOCEAN_TOKEN", SENTINEL_API_KEY)
    api_key_helpers.set_api_key(SENTINEL_API_KEY)
    return SENTINEL_API_KEY


@pytest.fixture(autouse=True)
def clear_local_env_var_for_test(monkeypatch: pytest.MonkeyPatch):
    """Ensure that the tests aren't infected by local env vars."""
    monkeypatch.delenv("DIGITALOCEAN_TOKEN", raising=False)
