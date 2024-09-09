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
                404,
                {"id": "not_found", "message": "The resource you requested could not be found."},
                id="invalid-top-domain",
            ),
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
        status_code: int,
        json_response: dict[str, str],
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


class TestCreateARecord:
    """We can create A records for given subdomain/domain pair."""

    @pytest.mark.parametrize(
        "expected_subdomain, expected_domain",
        [
            pytest.param("@", "example.com", id="short-subdomain"),
            pytest.param("support.example.com", "example.com", id="long-subdomain"),
        ],
    )
    def test_A_record_creation(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        expected_domain: str,
        expected_subdomain: str,
        capsys: pytest.CaptureFixture[str],
    ):
        """Given valid values, we can create an A record."""

        EXPECTED_IP_ADDRESS = "127.0.0.1"
        EXPECTED_A_RECORD_NAME = expected_subdomain.removesuffix("." + expected_domain)
        EXPECTED_DOMAIN_RECORD_ID = 10001

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.post(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.json_params_matcher(
                    {
                        "name": EXPECTED_A_RECORD_NAME,
                        "data": EXPECTED_IP_ADDRESS,
                        "type": "A",
                        "ttl": 3600,
                    }
                ),
            ],
            json={"domain_record": {"id": EXPECTED_DOMAIN_RECORD_ID}},
        )

        domain_record_id = do_api.create_A_record(
            expected_subdomain, expected_domain, EXPECTED_IP_ADDRESS
        )

        assert domain_record_id == EXPECTED_DOMAIN_RECORD_ID
        assert (
            f"An A record for {EXPECTED_A_RECORD_NAME}.{expected_domain} has been added."
            in capsys.readouterr().out
        )

    @pytest.mark.parametrize(
        "status_code, json_response",
        [
            pytest.param(
                404,
                {"id": "not_found", "message": "The resource you requested could not be found."},
                id="invalid-top-domain",
            ),
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
    def test_invalid_api_responses(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        status_code: int,
        json_response: dict[str, str],
    ):
        """HTTPErrors are raised."""
        EXPECTED_DOMAIN = "domain.example.com"
        EXPECTED_A_RECORD_NAME = "@"
        EXPECTED_IP_ADDRESS = "127.0.0.1"

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.post(
            url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.json_params_matcher(
                    {
                        "name": EXPECTED_A_RECORD_NAME,
                        "data": EXPECTED_IP_ADDRESS,
                        "type": "A",
                        "ttl": 3600,
                    }
                ),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            _ = do_api.create_A_record(EXPECTED_A_RECORD_NAME, EXPECTED_DOMAIN, EXPECTED_IP_ADDRESS)
