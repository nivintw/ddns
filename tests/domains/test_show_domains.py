# ddns-digital-ocean
# Copyright (C) 2023  Tyler Nivin <tyler@nivin.tech>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

import datetime as dt
from sqlite3 import Connection
from typing import Literal

import pytest
from responses import RequestsMock, matchers

from ddns_digital_ocean import domains


@pytest.mark.usefixtures("mock_db_for_test")
class TestListAllDomains:
    """We can show (up to 200) upstream domains."""

    def test_no_upstream_domains(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        capsys: pytest.CaptureFixture[str],
    ):
        """Ensure proper handling of response when no upstream domains are registered."""
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url="https://api.digitalocean.com/v2/domains/",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": 200}),
            ],
            json={"domains": [], "meta": {"total": 0}},
            status=200,
        )

        domains.show_all_domains()
        captured_output = capsys.readouterr()
        assert "No domains associated with this Digital Ocean account!" in captured_output.out

    def test_list_upstream_domains_output(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
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
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url="https://api.digitalocean.com/v2/domains/",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": 200}),
            ],
            json={
                "domains": [
                    {"name": "example.com", "ttl": 1800, "zone_file": "lorem ipsum"},  # not managed
                    {"name": "nivin.tech", "ttl": 1800, "zone_file": "lorem ipsum"},  # managed
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        domains.show_all_domains()
        captured_output = capsys.readouterr()
        assert "Name : nivin.tech [*]" in captured_output.out
        assert "Name : example.com" in captured_output.out
        assert "Name : example.com [*]" not in captured_output.out

    def test_multiple_pages_of_domains(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        capsys: pytest.CaptureFixture[str],
    ):
        """Proper handling when there is more than one page of results."""
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url="https://api.digitalocean.com/v2/domains/",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": 200}),
            ],
            json={
                "domains": [
                    {"name": "example.com", "ttl": 1800, "zone_file": "lorem ipsum"},
                ],
                "meta": {"total": 200},  # a convenient lie...
            },
            status=200,
        )
        mocked_responses.get(
            url="https://api.digitalocean.com/v2/domains/",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": 200, "page": 2}),
            ],
            json={
                "domains": [
                    {"name": "nivin.tech", "ttl": 1800, "zone_file": "lorem ipsum"},
                ],
                "meta": {"total": 1},
            },
            status=200,
        )
        domains.show_all_domains()
        captured_output = capsys.readouterr()
        assert "Name : nivin.tech" in captured_output.out
        assert "Name : nivin.tech [*]" not in captured_output.out
        assert "Name : example.com" in captured_output.out
        assert "Name : example.com [*]" not in captured_output.out
