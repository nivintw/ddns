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

from sqlite3 import Connection

import pytest
from pytest_mock import MockerFixture


@pytest.fixture()
def added_top_domain(
    mock_db_for_test: Connection,
    mocker: MockerFixture,
):
    """Inject a top-level domain into the test DB."""
    from digital_ocean_dynamic_dns import domains

    EXPECTED_TOP_DOMAIN = "example.com"
    mocked_verify_domain_registered = mocker.patch.object(
        domains.do_api, "verify_domain_is_registered", autospec=True
    )

    domains.manage_domain(EXPECTED_TOP_DOMAIN)

    yield EXPECTED_TOP_DOMAIN
    mocked_verify_domain_registered.assert_called_once_with(EXPECTED_TOP_DOMAIN)
