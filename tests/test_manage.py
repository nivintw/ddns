# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

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
        mocked_manage_all_existing_a_records = mocker.patch.object(
            manage.domains, "manage_all_existing_a_records", autospec=True
        )

        manage.martial_manage(test_args)
        # We always attempt to manage the top level domain
        # in order to prevent folks from _having_ to configure the top domain separately.
        mocked_manage_domain.assert_called_once_with(EXPECTED_DOMAIN)

        # Validate
        mocked_manage_all_existing_a_records.assert_called_once_with(domain=EXPECTED_DOMAIN)

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
