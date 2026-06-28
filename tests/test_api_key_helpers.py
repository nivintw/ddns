# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

import pytest

from digital_ocean_dynamic_dns import api_key_helpers


@pytest.mark.usefixtures("mock_db_for_test")
class TestApiKeyStorage:
    """We can store and lookup an API key in the database."""

    def test_lookup_no_api_key(self):
        """Validate behavior when we try to grab an API key but there is none."""

        with pytest.raises(api_key_helpers.NoAPIKeyError):
            api_key_helpers.get_api()

    def test_update_api_key(
        self,
        monkeypatch: pytest.MonkeyPatch,
        preload_api_key,
    ):
        """We can update the API if asked."""
        ORIGINAL_API_KEY = preload_api_key
        EXPECTED_API_KEY = "updated-api-key"  # pragma: allowlist secret
        monkeypatch.setenv("DIGITALOCEAN_TOKEN", EXPECTED_API_KEY)

        # Test
        found_api = api_key_helpers.get_api()

        # Validate: api key was updated
        assert found_api != ORIGINAL_API_KEY
        # validate: api key is new value
        assert found_api == EXPECTED_API_KEY
