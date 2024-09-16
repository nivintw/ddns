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
