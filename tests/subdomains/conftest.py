# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Shared fixtures for subdomain tests."""

from collections.abc import Generator

import pytest
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import domains


@pytest.fixture
def added_top_domain(
    mocker: MockerFixture,
) -> Generator[str, None, None]:
    """Inject a top-level domain into the test DB."""
    expected_top_domain = "example.com"
    mocked_verify_domain_registered = mocker.patch.object(
        domains.do_api, "verify_domain_is_registered", autospec=True
    )

    domains.manage_domain(expected_top_domain)

    yield expected_top_domain
    mocked_verify_domain_registered.assert_called_once_with(expected_top_domain)
