from pathlib import Path

import pytest
from pytest_check import check

from ddns_digital_ocean import api_key_helpers
from ddns_digital_ocean.database import connect_database


class TestApiKeyStorage:
    """We can store and lookup an API key in the database."""

    def test_lookup_no_api_key(self, temp_database_path: Path, mocker):
        """Validate behavior when we try to grab an API key but there is none."""
        test_specific_conn = connect_database(temp_database_path)
        mocker.patch.object(api_key_helpers, "conn", test_specific_conn)

        with pytest.raises(api_key_helpers.NoAPIKeyError):
            api_key_helpers.get_api()

    def test_store_retrieve_api_key(self, temp_database_path: Path, mocker):
        """Validate successful retrieval of an API key stored in the DB."""
        test_specific_conn = connect_database(temp_database_path)
        mocker.patch.object(api_key_helpers, "conn", test_specific_conn)

        EXPECTED_API_KEY = "fake-value-for-testing"  # pragma: allowlist secret

        # Arrange/Test: add an API key so we can test the lookup.
        api_key_helpers.api(EXPECTED_API_KEY)

        # Test: Lookup the API key we just inserted.
        found_api_key = api_key_helpers.get_api()
        with check:
            assert found_api_key == EXPECTED_API_KEY

    def test_update_api_key(self, temp_database_path: Path, mocker):
        """We can update the API if asked."""
        test_specific_conn = connect_database(temp_database_path)
        mocker.patch.object(api_key_helpers, "conn", test_specific_conn)

        ORIGINAL_API_KEY = "original-api-key"  # pragma: allowlist secret
        EXPECTED_API_KEY = "updated-api-key"  # pragma: allowlist secret

        with check:
            # Arrange: Store the original API key.
            api_key_helpers.api(ORIGINAL_API_KEY)
            # Arrange/validate: the initial key store functioned as expected.
            # NOTE: this is really just to guard against silent failures
            # and prove we are _changing_ the key; not just storing.
            pre_update_key = api_key_helpers.get_api()
            assert pre_update_key == ORIGINAL_API_KEY

            # Test Store new API key.
            api_key_helpers.api(EXPECTED_API_KEY)
            found_update_key = api_key_helpers.get_api()
            assert found_update_key == EXPECTED_API_KEY
