# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Tests for listing subdomains / A records via the subdomains module."""

from datetime import UTC, datetime
from sqlite3 import Connection
from typing import Literal

import pytest
import requests
import responses as responses_lib
from pytest_mock import MockerFixture
from responses import matchers

from digital_ocean_dynamic_dns import subdomains

# Fixtures all tests in this module will use.
pytestmark = pytest.mark.usefixtures("mock_db_for_test", "mocked_responses")

PAGE_RESULTS_LIMIT = 20


def test_domain_not_registered(
    preload_api_key: str,
    mocked_responses: responses_lib.RequestsMock,
) -> None:
    """Domain not associated with DO account."""
    expected_domain = "example.com"
    headers = {
        "Authorization": "Bearer " + preload_api_key,
        "Content-Type": "application/json",
    }
    # Arrange: mock a 404 response.
    mocked_responses.get(
        url=f"https://api.digitalocean.com/v2/domains/{expected_domain}/records",
        match=[
            matchers.header_matcher(headers),
            matchers.query_param_matcher({"per_page": PAGE_RESULTS_LIMIT, "type": "A"}),
        ],
        status=404,
    )
    # Validate: Ensure that the HTTP error is bubbled up / not swallowed.
    with pytest.raises(requests.HTTPError, match=r"404"):
        subdomains.list_sub_domains(expected_domain)


class TestDomainNotManaged:
    """Domain is wholly unmanaged."""

    def test_unmanaged_a_records(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Domain registered but not managed.

        Two A records registered for this domain.
        """
        expected_domain = "test.domain.example.com"
        expected_domain_records = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_a_records = mocker.patch.object(
            subdomains.do_api,
            "get_a_records",
            autospec=True,
        )
        mocked_get_a_records.return_value = expected_domain_records
        subdomains.list_sub_domains(expected_domain)

        mocked_get_a_records.assert_called_once_with(expected_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {expected_domain}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {expected_domain}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " in captured_errout
        for record in expected_domain_records:
            assert str(record["name"]) in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {expected_domain}" not in captured_errout

    def test_no_registered_a_records(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Domain registered but not managed.

        Two A records registered for this domain.
        """
        expected_domain = "test.domain.example.com"
        expected_domain_records: list[dict] = []
        mocked_get_a_records = mocker.patch.object(
            subdomains.do_api,
            "get_a_records",
            autospec=True,
        )
        mocked_get_a_records.return_value = expected_domain_records
        subdomains.list_sub_domains(expected_domain)

        mocked_get_a_records.assert_called_once_with(expected_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {expected_domain}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {expected_domain}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " not in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {expected_domain}" in captured_errout


class TestManagedDomain:
    """Top domain is managed; various states for subdomains/A records."""

    def test_no_a_records_registered(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Domain managed, no A records registered."""
        expected_domain_records: list[dict] = []
        mocked_get_a_records = mocker.patch.object(
            subdomains.do_api,
            "get_a_records",
            autospec=True,
        )
        mocked_get_a_records.return_value = expected_domain_records
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_a_records.assert_called_once_with(added_top_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {added_top_domain}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " not in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" in captured_errout

    def test_only_unmanaged_a_records(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A records exist, all are unmanaged."""
        expected_domain_records = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_a_records = mocker.patch.object(
            subdomains.do_api,
            "get_a_records",
            autospec=True,
        )
        mocked_get_a_records.return_value = expected_domain_records
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_a_records.assert_called_once_with(added_top_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {added_top_domain}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " in captured_errout
        for record in expected_domain_records:
            assert str(record["name"]) in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" not in captured_errout

    def test_mix_managed_unmanaged_a_records(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
        mock_db_for_test: Connection,
    ) -> None:
        """One managed A record, One unmanaged A record."""
        expected_domain_records = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            # support is marked unmanaged and in the DB.
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
            # test is not in the DB at all
            {"id": 3, "name": "test", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_a_records = mocker.patch.object(
            subdomains.do_api,
            "get_a_records",
            autospec=True,
        )
        mocked_get_a_records.return_value = expected_domain_records

        # Arrange: Insert one of the domain records into the database.
        with mock_db_for_test:
            top_domain_id = mock_db_for_test.execute(
                "select id from domains where name = ?", (added_top_domain,)
            ).fetchone()["id"]
            now = datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M")
            mock_db_for_test.execute(
                "INSERT INTO subdomains("
                "   domain_record_id,"
                "   main_id,"
                "   name,"
                "   current_ip4,"
                "   cataloged,"
                "   last_checked,"
                "   last_updated"
                ") values("
                "   :domain_record_id,"
                "   :main_id,"
                "   :name,"
                "   :current_ip4,"
                "   :cataloged,"
                "   :last_checked,"
                "   :last_updated"
                ")",
                {
                    "domain_record_id": expected_domain_records[0]["id"],
                    "main_id": top_domain_id,
                    "name": expected_domain_records[0]["name"],
                    "current_ip4": "127.0.0.1",
                    "cataloged": now,
                    "last_checked": now,
                    "last_updated": now,
                },
            )
            mock_db_for_test.execute(
                "INSERT INTO subdomains("
                "   domain_record_id,"
                "   main_id,"
                "   name,"
                "   current_ip4,"
                "   cataloged,"
                "   last_checked,"
                "   last_updated,"
                "   managed "
                ") values("
                "   :domain_record_id,"
                "   :main_id,"
                "   :name,"
                "   :current_ip4,"
                "   :cataloged,"
                "   :last_checked,"
                "   :last_updated,"
                "   0"
                ")",
                {
                    "domain_record_id": expected_domain_records[1]["id"],
                    "main_id": top_domain_id,
                    "name": expected_domain_records[1]["name"],
                    "current_ip4": "127.0.0.1",
                    "cataloged": now,
                    "last_checked": now,
                    "last_updated": now,
                },
            )

        # Test
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_a_records.assert_called_once_with(added_top_domain)
        captured_errout = " ".join(capsys.readouterr().out.split())

        # Validate lack of output string: Do not report no managed A records
        assert f"No managed A records for {added_top_domain}" not in captured_errout
        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" not in captured_errout

        managed_records_output, unmanaged_records_output = captured_errout.split(
            f"Unmanaged A records for {added_top_domain}"
        )
        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" in captured_errout
        assert expected_domain_records[0]["name"] in managed_records_output

        # Report: unmanaged and registered A records
        assert expected_domain_records[1]["name"] in unmanaged_records_output
        assert expected_domain_records[2]["name"] in unmanaged_records_output

    def test_all_managed_a_records(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
        mock_db_for_test: Connection,
    ) -> None:
        """All current A records are managed."""
        expected_domain_records = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_a_records = mocker.patch.object(
            subdomains.do_api,
            "get_a_records",
            autospec=True,
        )
        mocked_get_a_records.return_value = expected_domain_records

        # Arrange: Insert all expected domain records into the database.
        with mock_db_for_test:
            top_domain_id = mock_db_for_test.execute(
                "select id from domains where name = ?", (added_top_domain,)
            ).fetchone()["id"]
            now = datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M")
            for domain_record in expected_domain_records:
                mock_db_for_test.execute(
                    "INSERT INTO subdomains("
                    "   domain_record_id,"
                    "   main_id,"
                    "   name,"
                    "   current_ip4,"
                    "   cataloged,"
                    "   last_checked,"
                    "   last_updated"
                    ") values("
                    "   :domain_record_id,"
                    "   :main_id,"
                    "   :name,"
                    "   :current_ip4,"
                    "   :cataloged,"
                    "   :last_checked,"
                    "   :last_updated"
                    ")",
                    {
                        "domain_record_id": domain_record["id"],
                        "main_id": top_domain_id,
                        "name": domain_record["name"],
                        "current_ip4": "127.0.0.1",
                        "cataloged": now,
                        "last_checked": now,
                        "last_updated": now,
                    },
                )

        # Test
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_a_records.assert_called_once_with(added_top_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {added_top_domain}" not in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" in captured_errout
        for record in expected_domain_records:
            assert str(record["name"]) in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " not in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" in captured_errout
