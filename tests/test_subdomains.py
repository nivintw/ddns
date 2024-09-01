# ddns-digital-ocean
# Copyright (C) 2023  Tyler Nivin <tyler@nivin.tech>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

import sqlite3
from pathlib import Path
from sqlite3 import Connection

import pytest

from ddns_digital_ocean import api_key_helpers, domains
from ddns_digital_ocean.database import connect_database


@pytest.fixture()
def mock_db_for_test(temp_database_path: Path, mocker):
    """Mock api_key_helpers.conn to have a per-test connection / database.
    Ensures isolation of the database state between tests.

    In this module we have to mock out the conn objects everywhere they are created
      in order to ensure all modules/functions are using the same databases.

    """
    test_specific_conn = connect_database(temp_database_path)
    test_specific_conn.row_factory = sqlite3.Row
    mocker.patch.object(domains, "conn", test_specific_conn)
    mocker.patch.object(api_key_helpers, "conn", test_specific_conn)

    return test_specific_conn


@pytest.fixture()
def preload_api_key(mock_db_for_test: Connection):
    """Load a sentinel API key.
    Almost all operations require an api key to be configured.
    This fixture provides a sentinel / not-real API key for us to use.
    """
    SENTINEL_API_KEY = "sentinel-api-key"  # pragma: allowlist secret
    api_key_helpers.set_api_key(SENTINEL_API_KEY)
    return SENTINEL_API_KEY


class TestToggleSubdomainManagement:
    """We can toggle management of specific subdomains on and off.
    The result state is the inverse of the current state.
    I.e. managed -> unmanaged and unmanaged -> managed.
    """

    def test_inverse_result_status(
        self,
        mock_db_for_test: Connection,
    ):
        """Toggling a subdomain results in the inverse manage state."""
        ...

    def test_toggle_subdomain_not_added(
        self,
        mock_db_for_test: Connection,
    ):
        """Trying to toggle a subdomain that is not locally registered informs user."""
        ...
