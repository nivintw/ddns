# ddns-digital-ocean
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
#   and the ddns-digital-ocean contributors

import datetime as dt
from sqlite3 import Connection

import pytest
from pytest_mock import MockerFixture

from ddns_digital_ocean import args, domains


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
    ):
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
    ):
        """Validate output for upstream domains.

        Properly marks both ddns-digital-ocean managed domains as well as
        domains that exist upstream that are not managed by ddns-digital-ocean.
        """

        # Arrange: insert records into the DB to show nivin.tech as managed by ddns-digital-ocean
        with mock_db_for_test:
            update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
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
