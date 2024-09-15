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
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import args, manage

pytestmark = pytest.mark.usefixtures("mocked_responses", "mock_db_for_test")


class TestMartialManage:
    """Martial the behavior based on args."""

    def test_list_subdomains(self, mocker: MockerFixture):
        """Test listing subdomains via argparse"""
        EXPECTED_DOMAIN = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["manage", EXPECTED_DOMAIN, "--list"])

        # Mock manage_domain; just ensure it was called.
        mocked_manage_domain = mocker.patch.object(manage.domains, "manage_domain", autospec=True)

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_list_sub_domains = mocker.patch.object(
            manage.subdomains, "list_sub_domains", autospec=True
        )

        manage.martial_manage(test_args)
        # We always attempt to manage the top level domain
        # in order to prevent folks from _having_ to configure the top domain separately.
        mocked_manage_domain.assert_called_once_with(EXPECTED_DOMAIN)

        # Validate
        mocked_list_sub_domains.assert_called_once_with(EXPECTED_DOMAIN)

    def test_manage_entire_domain(
        self,
        mocker,
    ):
        """If called without --subdomain, manage all existing A records for `domain`."""
        EXPECTED_DOMAIN = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["manage", EXPECTED_DOMAIN])

        # Mock manage_domain; just ensure it was called.
        mocked_manage_domain = mocker.patch.object(manage.domains, "manage_domain", autospec=True)

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_manage_all_existing_A_records = mocker.patch.object(
            manage.domains, "manage_all_existing_A_records", autospec=True
        )

        manage.martial_manage(test_args)
        # We always attempt to manage the top level domain
        # in order to prevent folks from _having_ to configure the top domain separately.
        mocked_manage_domain.assert_called_once_with(EXPECTED_DOMAIN)

        # Validate
        mocked_manage_all_existing_A_records.assert_called_once_with(domain=EXPECTED_DOMAIN)

    def test_manage_specific_subdomain(
        self,
        mocker: MockerFixture,
    ):
        """--subdomain results in managing _just_ that subdomain."""
        EXPECTED_DOMAIN = "example.com"
        EXPECTED_SUBDOMAIN = "support"

        parser = args.setup_argparse()
        test_args = parser.parse_args(
            args=["manage", EXPECTED_DOMAIN, "--subdomain", EXPECTED_SUBDOMAIN]
        )

        # Mock manage_domain; just ensure it was called.
        mocked_manage_domain = mocker.patch.object(manage.domains, "manage_domain", autospec=True)

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_manage_subdomain = mocker.patch.object(
            manage.subdomains, "manage_subdomain", autospec=True
        )

        manage.martial_manage(test_args)
        # We always attempt to manage the top level domain
        # in order to prevent folks from _having_ to configure the top domain separately.
        mocked_manage_domain.assert_called_once_with(EXPECTED_DOMAIN)

        # Validate
        mocked_manage_subdomain.assert_called_once_with(
            subdomain=EXPECTED_SUBDOMAIN, domain=EXPECTED_DOMAIN
        )


class TestMartialUnManage:
    """Martial the behavior based on args."""

    def test_list_subdomains(self, mocker: MockerFixture):
        """Test listing subdomains via argparse"""
        EXPECTED_DOMAIN = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["un-manage", EXPECTED_DOMAIN, "--list"])

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_list_sub_domains = mocker.patch.object(
            manage.subdomains, "list_sub_domains", autospec=True
        )

        manage.martial_un_manage(test_args)

        # Validate
        mocked_list_sub_domains.assert_called_once_with(EXPECTED_DOMAIN)

    def test_un_manage_entire_domain(
        self,
        mocker,
    ):
        """If called without --subdomain, stop managing all managed A records for `domain`."""
        EXPECTED_DOMAIN = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["un-manage", EXPECTED_DOMAIN])

        # Mock manage_domain; just ensure it was called.
        mocked_un_manage_domain = mocker.patch.object(
            manage.domains, "un_manage_domain", autospec=True
        )

        manage.martial_un_manage(test_args)
        # We always attempt to manage the top level domain
        # in order to prevent folks from _having_ to configure the top domain separately.

        # Validate
        mocked_un_manage_domain.assert_called_once_with(domain=EXPECTED_DOMAIN)

    def test_un_manage_specific_subdomain(
        self,
        mocker: MockerFixture,
    ):
        """--subdomain results in managing _just_ that subdomain."""
        EXPECTED_DOMAIN = "example.com"
        EXPECTED_SUBDOMAIN = "support"

        parser = args.setup_argparse()
        test_args = parser.parse_args(
            args=["un-manage", EXPECTED_DOMAIN, "--subdomain", EXPECTED_SUBDOMAIN]
        )

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_un_manage_subdomain = mocker.patch.object(
            manage.subdomains, "un_manage_subdomain", autospec=True
        )

        manage.martial_un_manage(test_args)

        # Validate
        mocked_un_manage_subdomain.assert_called_once_with(
            subdomain=EXPECTED_SUBDOMAIN, domain=EXPECTED_DOMAIN
        )
