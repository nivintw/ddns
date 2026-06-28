# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for the show-info domains command."""

import datetime as dt
from sqlite3 import Connection

import pytest
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import args, domains


@pytest.mark.usefixtures("mock_db_for_test", "mocked_responses")
class TestListAllDomains:
    """We can show all upstream domains.

    Assumptions:
        1. upstream do_api functions handle pagination and return iterables
    """

    def test_no_upstream_domains(
        self,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
    ) -> None:
        """Ensure proper handling of response when no upstream domains are registered."""
        mocked_get_all_domains = mocker.patch.object(
            domains.do_api, "get_all_domains", autospec=True
        )
        mocked_get_all_domains.return_value = []  # no domains
        parser = args.setup_argparse()
        test_args = parser.parse_args(["show-info", "domains"])
        test_args.func(test_args)

        captured_output = capsys.readouterr()
        assert "No domains associated with this Digital Ocean account!" in captured_output.out

    def test_list_upstream_domains_output(
        self,
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
    ) -> None:
        """Validate output for upstream domains.

        Properly marks both ddns-digital-ocean managed domains as well as
        domains that exist upstream that are not managed by ddns-digital-ocean.
        """
        # Arrange: insert records into the DB to show nivin.tech as managed by ddns-digital-ocean
        with mock_db_for_test:
            update_datetime = dt.datetime.now(tz=dt.UTC).astimezone().strftime("%Y-%m-%d %H:%M")
            mock_db_for_test.execute(
                "INSERT INTO domains(name, cataloged, last_managed) "
                " values(:name, :cataloged, :last_managed)",
                {
                    "name": "nivin.tech",
                    "cataloged": update_datetime,
                    "last_managed": update_datetime,
                },
            )

        mocked_get_all_domains = mocker.patch.object(
            domains.do_api, "get_all_domains", autospec=True
        )
        mocked_get_all_domains.return_value = [
            {"name": "example.com", "ttl": 1800, "zone_file": "lorem ipsum"},  # not managed
            {"name": "nivin.tech", "ttl": 1800, "zone_file": "lorem ipsum"},  # managed
        ]

        parser = args.setup_argparse()
        test_args = parser.parse_args(["show-info", "domains"])
        test_args.func(test_args)

        captured_output = capsys.readouterr()
        assert "Name : nivin.tech [*]" in captured_output.out
        assert "Name : example.com" in captured_output.out
        assert "Name : example.com [*]" not in captured_output.out
