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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech> and the ddns-digital-ocean contributors

from pathlib import Path

import pytest
from pytest_check import check

from ddns_digital_ocean import api_key_helpers
from ddns_digital_ocean.database import connect_database


@pytest.fixture()
def mock_db_for_test(temp_database_path: Path, mocker):
    """Mock api_key_helpers.conn to have a per-test connection / database.
    Ensures isolation of the database state between tests.
    """
    test_specific_conn = connect_database(temp_database_path)
    mocker.patch.object(api_key_helpers, "conn", test_specific_conn)


@pytest.mark.usefixtures("mock_db_for_test")
class TestApiKeyStorage:
    """We can store and lookup an API key in the database."""

    def test_lookup_no_api_key(self):
        """Validate behavior when we try to grab an API key but there is none."""

        with pytest.raises(api_key_helpers.NoAPIKeyError):
            api_key_helpers.get_api()

    def test_store_retrieve_api_key(self):
        """Validate successful retrieval of an API key stored in the DB."""

        EXPECTED_API_KEY = "fake-value-for-testing"  # pragma: allowlist secret

        # Arrange/Test: add an API key so we can test the lookup.
        api_key_helpers.set_api_key(EXPECTED_API_KEY)

        # Test: Lookup the API key we just inserted.
        found_api_key = api_key_helpers.get_api()
        with check:
            assert found_api_key == EXPECTED_API_KEY

    def test_update_api_key(self):
        """We can update the API if asked."""

        ORIGINAL_API_KEY = "original-api-key"  # pragma: allowlist secret
        EXPECTED_API_KEY = "updated-api-key"  # pragma: allowlist secret

        with check:
            # Arrange: Store the original API key.
            api_key_helpers.set_api_key(ORIGINAL_API_KEY)
            # Arrange/validate: the initial key store functioned as expected.
            # NOTE: this is really just to guard against silent failures
            # and prove we are _changing_ the key; not just storing.
            pre_update_key = api_key_helpers.get_api()
            assert pre_update_key == ORIGINAL_API_KEY

            # Test Store new API key.
            api_key_helpers.set_api_key(EXPECTED_API_KEY)
            found_update_key = api_key_helpers.get_api()
            assert found_update_key == EXPECTED_API_KEY
