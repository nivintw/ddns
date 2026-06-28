# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

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
