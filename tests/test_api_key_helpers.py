# ddns-digital-ocean
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
#   and the ddns-digital-ocean contributors

from pathlib import Path

import pytest
from pytest_check import check

from ddns_digital_ocean import api_key_helpers
from ddns_digital_ocean.database import connect_database

# TODO add checks for last_updated column behavior.


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
