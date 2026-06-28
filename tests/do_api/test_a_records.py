# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for DigitalOcean API A-record CRUD operations."""

from itertools import repeat
from typing import Literal

import pytest
import requests
from responses import RequestsMock, matchers

from digital_ocean_dynamic_dns import do_api


class TestGetARecords:
    """We can retrieve all A records for the provided domain."""

    # Constants common to get_a_records()
    PAGE_RESULTS_LIMIT = 20

    def test_single_page(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """Simple A record retrieval validation."""
        expected_domain = "test.domain.example.com"
        expected_domain_records = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json={
                "domain_records": expected_domain_records,
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(expected_domain_records)},
            },
        )

        domain_records = list(do_api.get_a_records(expected_domain))
        assert domain_records == expected_domain_records

    def test_no_existing_a_records(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """When no A records are available, raise no errors; return empty generator."""
        expected_domain = "test.domain.example.com"
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json={"domain_records": [], "meta": {"total": 0}},
        )

        with pytest.raises(StopIteration):
            next(do_api.get_a_records(expected_domain))

    def test_multiple_pages(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """Pagination is supported."""
        expected_domain = "test.domain.example.com"
        expected_domain_records = [
            *list(
                repeat(
                    {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
                    self.PAGE_RESULTS_LIMIT,
                )
            ),
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json={
                "domain_records": expected_domain_records[: self.PAGE_RESULTS_LIMIT],
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(expected_domain_records)},
            },
        )
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {"per_page": self.PAGE_RESULTS_LIMIT, "page": 2, "type": "A"}
                ),
            ],
            json={
                "domain_records": expected_domain_records[self.PAGE_RESULTS_LIMIT :],
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(expected_domain_records)},
            },
        )

        domain_records = list(do_api.get_a_records(expected_domain))
        assert domain_records == expected_domain_records

    @pytest.mark.parametrize(
        ("status_code", "json_response"),
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
    ) -> None:
        """Invalid responses are raised.

        This includes if the domain specified can't be found.
        """
        expected_domain = "test.domain.example.com"

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher({"per_page": self.PAGE_RESULTS_LIMIT, "type": "A"}),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            next(do_api.get_a_records(expected_domain))


class TestGetARecordsByName:
    """We can retrieve all A records matching provided name for the provided domain.

    Normally, we'd probably expect only one matching result, but technically this
    request could return multiple matches as there is nothing stopping you from
    creating multiple records with the same name.
    """

    # Constants common to get_a_record_by_name()
    PAGE_RESULTS_LIMIT = 20

    def test_single_page(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """Simple A record retrieval validation."""
        expected_domain = "test.domain.example.com"
        expected_subdomain = "@"
        expected_domain_records = [
            {"id": 1, "name": expected_subdomain, "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": expected_subdomain, "data": "127.0.0.1", "ttl": 1800},
        ]
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {
                        "name": f"{expected_subdomain}.{expected_domain}",
                        "per_page": self.PAGE_RESULTS_LIMIT,
                        "type": "A",
                    }
                ),
            ],
            json={
                "domain_records": expected_domain_records,
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(expected_domain_records)},
            },
        )

        domain_records = list(do_api.get_a_record_by_name(expected_subdomain, expected_domain))
        assert domain_records == expected_domain_records

    def test_no_matching_a_records(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """When no A records are available, raise no errors; return empty generator."""
        expected_domain = "test.domain.example.com"
        expected_subdomain = "@"
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {
                        "name": f"{expected_subdomain}.{expected_domain}",
                        "per_page": self.PAGE_RESULTS_LIMIT,
                        "type": "A",
                    }
                ),
            ],
            json={"domain_records": [], "meta": {"total": 0}},
        )

        with pytest.raises(StopIteration):
            next(do_api.get_a_record_by_name(expected_subdomain, expected_domain))

    def test_multiple_pages(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """Pagination is supported."""
        expected_domain = "test.domain.example.com"
        expected_subdomain = "@"
        expected_domain_records = [
            *list(
                repeat(
                    {"id": 1, "name": expected_subdomain, "data": "127.0.0.1", "ttl": 1800},
                    self.PAGE_RESULTS_LIMIT,
                )
            ),
            {"id": 2, "name": expected_subdomain, "data": "127.0.0.1", "ttl": 1800},
        ]
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {
                        "name": f"{expected_subdomain}.{expected_domain}",
                        "per_page": self.PAGE_RESULTS_LIMIT,
                        "type": "A",
                    }
                ),
            ],
            json={
                "domain_records": expected_domain_records[: self.PAGE_RESULTS_LIMIT],
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(expected_domain_records)},
            },
        )
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {
                        "name": f"{expected_subdomain}.{expected_domain}",
                        "per_page": self.PAGE_RESULTS_LIMIT,
                        "page": 2,
                        "type": "A",
                    }
                ),
            ],
            json={
                "domain_records": expected_domain_records[self.PAGE_RESULTS_LIMIT :],
                # Match observed DO api behavior; total returns TOTAL,
                # not total for this response; despite what docs say...
                # I reported to DO via a ticket.
                "meta": {"total": len(expected_domain_records)},
            },
        )

        domain_records = list(do_api.get_a_record_by_name(expected_subdomain, expected_domain))
        assert domain_records == expected_domain_records

    @pytest.mark.parametrize(
        ("status_code", "json_response"),
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
    ) -> None:
        """Invalid responses are raised.

        This includes if the domain specified can't be found.
        """
        expected_domain = "test.domain.example.com"
        expected_subdomain = "@"

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
            match=[
                matchers.header_matcher(headers),
                matchers.query_param_matcher(
                    {
                        "name": f"{expected_subdomain}.{expected_domain}",
                        "per_page": self.PAGE_RESULTS_LIMIT,
                        "type": "A",
                    }
                ),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            next(do_api.get_a_record_by_name(expected_subdomain, expected_domain))


class TestCreateARecord:
    """We can create A records for given subdomain/domain pair."""

    @pytest.mark.parametrize(
        ("expected_subdomain", "expected_domain"),
        [
            pytest.param("@", "example.com", id="short-subdomain"),
            pytest.param("support.example.com", "example.com", id="long-subdomain"),
        ],
    )
    def test_a_record_creation(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
        expected_domain: str,
        expected_subdomain: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Given valid values, we can create an A record."""
        expected_ip_address = "127.0.0.1"
        expected_a_record_name = expected_subdomain.removesuffix("." + expected_domain)
        expected_domain_record_id = 10001

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
                        "name": expected_a_record_name,
                        "data": expected_ip_address,
                        "type": "A",
                        "ttl": 3600,
                    }
                ),
            ],
            json={"domain_record": {"id": expected_domain_record_id}},
        )

        domain_record_id = do_api.create_a_record(
            expected_subdomain, expected_domain, expected_ip_address
        )

        assert domain_record_id == expected_domain_record_id
        assert (
            f"An A record for {expected_a_record_name}.{expected_domain} has been added."
            in capsys.readouterr().out
        )

    @pytest.mark.parametrize(
        ("status_code", "json_response"),
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
    ) -> None:
        """HTTPErrors are raised."""
        expected_domain = "domain.example.com"
        expected_a_record_name = "@"
        expected_ip_address = "127.0.0.1"

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
                        "name": expected_a_record_name,
                        "data": expected_ip_address,
                        "type": "A",
                        "ttl": 3600,
                    }
                ),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            _ = do_api.create_a_record(expected_a_record_name, expected_domain, expected_ip_address)

    @pytest.mark.parametrize(
        ("subdomain", "domain"),
        [
            pytest.param("@", "\N{GREEK CAPITAL LETTER DELTA}-forge.example.com", id="bad-domain"),
            pytest.param(
                "\N{GREEK CAPITAL LETTER DELTA}-forge.example.com",
                "example.com",
                id="bad-subdomain",
            ),
            pytest.param(
                "\N{GREEK CAPITAL LETTER DELTA}-forge.example.com",
                "\N{GREEK CAPITAL LETTER DELTA}-forge.example.com",
                id="both-bad",
            ),
        ],
    )
    def test_non_simple_chars_in_domain_name(
        self,
        subdomain: str,
        domain: str,
    ) -> None:
        """Raise NonSimpleDomainNameError if non-simple characters are used."""
        expected_ip_address = "127.0.0.1"
        with pytest.raises(do_api.NonSimpleDomainNameError):
            do_api.create_a_record(
                subdomain,
                domain,
                expected_ip_address,
            )


class TestGetARecord:
    """Retrieve a single A record."""

    def test_a_record_lookup(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """Retrieve a single A record."""
        expected_domain = "domain.example.com"
        expected_domain_record_id = 10_001
        expected_domain_record = {
            "id": expected_domain_record_id,
            "type": "A",
            "name": "@",
            "data": "127.0.0.1",
            "ttl": 1800,
        }

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records/{expected_domain_record_id}",
            match=[
                matchers.header_matcher(headers),
            ],
            json={"domain_record": expected_domain_record},
        )

        domain_record = do_api.get_a_record(str(expected_domain_record_id), expected_domain)
        assert domain_record == expected_domain_record

    @pytest.mark.parametrize(
        ("status_code", "json_response"),
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
    ) -> None:
        """HTTPErrors are raised."""
        expected_domain = "domain.example.com"
        expected_domain_record_id = 10_001

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.get(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records/{expected_domain_record_id}",
            match=[
                matchers.header_matcher(headers),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            _ = do_api.get_a_record(str(expected_domain_record_id), expected_domain)


class TestUpdateARecord:
    """Update an existing A record."""

    def test_update_a_record(
        self,
        mocked_responses: RequestsMock,
        preload_api_key: Literal["sentinel-api-key"],
    ) -> None:
        """Update an existing A record."""
        expected_domain = "domain.example.com"
        expected_domain_record_id = 10_001
        expected_ip_address = "127.0.0.1"
        expected_domain_record = {
            "id": expected_domain_record_id,
            "type": "A",
            "data": expected_ip_address,
        }

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.patch(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records/{expected_domain_record_id}",
            match=[
                matchers.header_matcher(headers),
                matchers.json_params_matcher(
                    {
                        "data": expected_ip_address,
                        "type": "A",
                    }
                ),
            ],
            json={"domain_record": expected_domain_record},
        )

        domain_record = do_api.update_a_record(
            str(expected_domain_record_id), expected_domain, expected_ip_address
        )
        assert domain_record == expected_domain_record

    @pytest.mark.parametrize(
        ("status_code", "json_response"),
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
    ) -> None:
        """HTTPErrors are raised."""
        expected_domain = "domain.example.com"
        expected_domain_record_id = 10_001
        expected_ip_address = "127.0.0.1"

        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        mocked_responses.patch(
            url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records/{expected_domain_record_id}",
            match=[
                matchers.header_matcher(headers),
                matchers.json_params_matcher(
                    {
                        "data": expected_ip_address,
                        "type": "A",
                    }
                ),
            ],
            json=json_response,
            status=status_code,
        )

        with pytest.raises(requests.exceptions.HTTPError, match=rf"{status_code}"):
            _ = do_api.update_a_record(
                str(expected_domain_record_id), expected_domain, expected_ip_address
            )
