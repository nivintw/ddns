# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for api_key_helpers module."""

import pytest

from digital_ocean_dynamic_dns import api_key_helpers


@pytest.mark.usefixtures("mock_db_for_test")
class TestApiKeyStorage:
    """We can store and lookup an API key in the database."""

    def test_lookup_no_api_key(self) -> None:
        """Validate behavior when we try to grab an API key but there is none."""
        with pytest.raises(api_key_helpers.NoAPIKeyError):
            api_key_helpers.get_api()

    def test_update_api_key(
        self,
        monkeypatch: pytest.MonkeyPatch,
        preload_api_key: str,
    ) -> None:
        """We can update the API if asked."""
        original_api_key = preload_api_key
        expected_api_key = "updated-api-key"  # pragma: allowlist secret
        monkeypatch.setenv("DIGITALOCEAN_TOKEN", expected_api_key)

        # Test
        found_api = api_key_helpers.get_api()

        # Validate: api key was updated
        assert found_api != original_api_key
        # validate: api key is new value
        assert found_api == expected_api_key
