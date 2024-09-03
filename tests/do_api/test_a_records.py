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

from itertools import repeat
from typing import Literal

import pytest
import requests
from responses import RequestsMock, matchers

from ddns_digital_ocean import do_api


class TestGetARecords:
    """We can retrieve all A records for the provided domain."""

    # Constants common to get_A_records()
    PAGE_RESULTS_LIMIT = 20

    def test_single_page(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ):
        """Simple A record retrieval validation."""
        EXPECTED_DOMAIN = "test.domain.example.com"
        EXPECTED_DOMAIN_RECORDS = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json={
                "domain_records": EXPECTED_DOMAIN_RECORDS,
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(EXPECTED_DOMAIN_RECORDS)},
            },
        )

        domain_records = [x for x in do_api.get_A_records(EXPECTED_DOMAIN)]
        assert domain_records == EXPECTED_DOMAIN_RECORDS

    def test_no_existing_a_records(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ):
        """When no A records are available, raise no errors; return empty generator."""
        EXPECTED_DOMAIN = "test.domain.example.com"
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json={"domain_records": [], "meta": {"total": 0}},
        )

        with pytest.raises(StopIteration):
            next(do_api.get_A_records(EXPECTED_DOMAIN))

    def test_multiple_pages(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ):
        """Pagination is supported."""
        EXPECTED_DOMAIN = "test.domain.example.com"
        EXPECTED_DOMAIN_RECORDS = [
            *[
                x
                for x in repeat(
                    {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
                    self.PAGE_RESULTS_LIMIT,
                )
            ],
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json={
                "domain_records": EXPECTED_DOMAIN_RECORDS[: self.PAGE_RESULTS_LIMIT],
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(EXPECTED_DOMAIN_RECORDS)},
            },
        )
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {"per_page": self.PAGE_RESULTS_LIMIT, "page": 2, "type": "A"}
                ),
            ],
            json={
                "domain_records": EXPECTED_DOMAIN_RECORDS[self.PAGE_RESULTS_LIMIT :],
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(EXPECTED_DOMAIN_RECORDS)},
            },
        )

        domain_records = [x for x in do_api.get_A_records(EXPECTED_DOMAIN)]
        assert domain_records == EXPECTED_DOMAIN_RECORDS

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
    def test_invalid_responses(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        status_code,
        json_response,
    ):
        """Invalid responses are raised.
        This includes if the domain specified can't be found.
        """
        EXPECTED_DOMAIN = "test.domain.example.com"

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            next(do_api.get_A_records(EXPECTED_DOMAIN))
