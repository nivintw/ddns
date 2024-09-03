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
import requests
from responses import RequestsMock, matchers

from ddns_digital_ocean import do_api


class TestGetAllDomains:
    """Retrieve all domains associated with an account."""

    def test_no_upstream_domains(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
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

        with pytest.raises(StopIteration):
            next(do_api.get_all_domains())

    def test_list_upstream_domains_output(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        mock_db_for_test: Connection,
    ):
        """Validate output for upstream domains.

        Properly marks both ddns-digital-ocean managed domains as well as
        domains that exist upstream that are not managed by ddns-digital-ocean.
        """

        EXPECTED_DOMAINS = [
            {"name": "example.com", "ttl": 1800, "zone_file": "lorem ipsum"},  # not managed
            {"name": "nivin.tech", "ttl": 1800, "zone_file": "lorem ipsum"},  # managed
        ]

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
                "domains": EXPECTED_DOMAINS,
                "meta": {"total": 2},
            },
            status=200,
        )

        domains = [x for x in do_api.get_all_domains()]
        assert domains == EXPECTED_DOMAINS

    def test_multiple_pages_of_domains(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ):
        """Proper handling when there is more than one page of results."""
        EXPECTED_DOMAINS = [
            {"name": "example.com", "ttl": 1800, "zone_file": "lorem ipsum"},
            {"name": "nivin.tech", "ttl": 1800, "zone_file": "lorem ipsum"},
        ]
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
                    EXPECTED_DOMAINS[0],
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
                    EXPECTED_DOMAINS[1],
                ],
                "meta": {"total": 1},
            },
            status=200,
        )
        domains = [x for x in do_api.get_all_domains()]
        assert domains == EXPECTED_DOMAINS


class TestVerifyDomainIsRegistered:
    """We can verify that the user-provided domain is valid."""

    def test_valid_domain(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ):
        """No exceptions raised when domain exist."""
        EXPECTED_DOMAIN = "test.domain.example.com"
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}",
            match=[
                matchers.header_matcher(headers),
            ],
            status=200,
            json={"name": EXPECTED_DOMAIN, "ttl": 1800, "zone_file": "lorem ipsum"},
        )
        # Test: As long as no exception is raised, we pass.
        do_api.verify_domain_is_registered(EXPECTED_DOMAIN)

    def test_missing_domain(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        capsys: pytest.CaptureFixture[str],
    ):
        """When domain is not found, we notify the user."""
        EXPECTED_DOMAIN = "test.domain.example.com"
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}",
            match=[
                matchers.header_matcher(headers),
            ],
            status=404,
            json={"id": "not_found", "message": "The resource you requested could not be found."},
        )
        with pytest.raises(requests.exceptions.HTTPError, match=r"404"):
            do_api.verify_domain_is_registered(EXPECTED_DOMAIN)

        cap_outerr = capsys.readouterr()
        assert (
            "was not found associated with this digital ocean account."
            in cap_outerr.out.replace("\n", "")
        )

    @pytest.mark.parametrize(
        "status_code, json_response",
        [
            pytest.param(
                401,
                {"id": "unauthorized", "message": "Unable to authenticate you."},
                id="unauthorized",
            ),
            pytest.param(
                429,
                {"id": "too_many_requests", "message": "API Rate limit exceeded."},
                id="too_many_requests",
            ),
            pytest.param(
                500,
                {"id": "server_error", "message": "Unexpected server-side error"},
                id="server_error",
            ),
        ],
    )
    def test_handle_DO_documented_error_responses(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        status_code,
        json_response,
    ):
        """We raise an exception for all other DO error responses."""
        EXPECTED_DOMAIN = "test.domain.example.com"
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}",
            match=[
                matchers.header_matcher(headers),
            ],
            status=status_code,
            json=json_response,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            do_api.verify_domain_is_registered(EXPECTED_DOMAIN)
