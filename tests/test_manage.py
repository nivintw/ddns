# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for the manage module's argument-dispatch logic."""

import pytest
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import args, manage

pytestmark = pytest.mark.usefixtures("mocked_responses", "mock_db_for_test")


class TestMartialManage:
    """Martial the behavior based on args."""

    def test_list_subdomains(self, mocker: MockerFixture) -> None:
        """Test listing subdomains via argparse."""
        expected_domain = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["manage", expected_domain, "--list"])

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
        mocked_manage_domain.assert_called_once_with(expected_domain)

        # Validate
        mocked_list_sub_domains.assert_called_once_with(expected_domain)

    def test_manage_entire_domain(
        self,
        mocker: MockerFixture,
    ) -> None:
        """If called without --subdomain, manage all existing A records for `domain`."""
        expected_domain = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["manage", expected_domain])

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
        mocked_manage_domain.assert_called_once_with(expected_domain)

        # Validate
        mocked_manage_all_existing_a_records.assert_called_once_with(domain=expected_domain)

    def test_manage_specific_subdomain(
        self,
        mocker: MockerFixture,
    ) -> None:
        """--subdomain results in managing _just_ that subdomain."""
        expected_domain = "example.com"
        expected_subdomain = "support"

        parser = args.setup_argparse()
        test_args = parser.parse_args(
            args=["manage", expected_domain, "--subdomain", expected_subdomain]
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
        mocked_manage_domain.assert_called_once_with(expected_domain)

        # Validate
        mocked_manage_subdomain.assert_called_once_with(
            subdomain=expected_subdomain, domain=expected_domain
        )


class TestMartialUnManage:
    """Martial the behavior based on args."""

    def test_list_subdomains(self, mocker: MockerFixture) -> None:
        """Test listing subdomains via argparse."""
        expected_domain = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["un-manage", expected_domain, "--list"])

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_list_sub_domains = mocker.patch.object(
            manage.subdomains, "list_sub_domains", autospec=True
        )

        manage.martial_un_manage(test_args)

        # Validate
        mocked_list_sub_domains.assert_called_once_with(expected_domain)

    def test_un_manage_entire_domain(
        self,
        mocker: MockerFixture,
    ) -> None:
        """If called without --subdomain, stop managing all managed A records for `domain`."""
        expected_domain = "example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["un-manage", expected_domain])

        # Mock manage_domain; just ensure it was called.
        mocked_un_manage_domain = mocker.patch.object(
            manage.domains, "un_manage_domain", autospec=True
        )

        manage.martial_un_manage(test_args)
        # We always attempt to manage the top level domain
        # in order to prevent folks from _having_ to configure the top domain separately.

        # Validate
        mocked_un_manage_domain.assert_called_once_with(domain=expected_domain)

    def test_un_manage_specific_subdomain(
        self,
        mocker: MockerFixture,
    ) -> None:
        """--subdomain results in managing _just_ that subdomain."""
        expected_domain = "example.com"
        expected_subdomain = "support"

        parser = args.setup_argparse()
        test_args = parser.parse_args(
            args=["un-manage", expected_domain, "--subdomain", expected_subdomain]
        )

        # Mock the call to list_sub_domains; we just want to be sure that it _is_ called,
        # but don't need it to run here.
        mocked_un_manage_subdomain = mocker.patch.object(
            manage.subdomains, "un_manage_subdomain", autospec=True
        )

        manage.martial_un_manage(test_args)

        # Validate
        mocked_un_manage_subdomain.assert_called_once_with(
            subdomain=expected_subdomain, domain=expected_domain
        )
