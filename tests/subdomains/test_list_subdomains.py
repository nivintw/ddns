# digital-ocean-dynamic-dns
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
#   and the digital-ocean-dynamic-dns contributors

from datetime import datetime
from sqlite3 import Connection
from typing import Literal

import pytest
import requests
from pytest_mock import MockerFixture
from responses import matchers

from digital_ocean_dynamic_dns import subdomains

# Fixtures all tests in this module will use.
pytestmark = pytest.mark.usefixtures("mock_db_for_test", "mocked_responses")

PAGE_RESULTS_LIMIT = 20


def test_domain_not_registered(
    preload_api_key,
    mocked_responses,
):
    """Domain not associated with DO account."""
    EXPECTED_DOMAIN = "example.com"
    headers = {
        "Authorization": "Bearer " + preload_api_key,
        "Content-Type": "application/json",
    }
    # Arrange: mock a 404 response.
    mocked_responses.get(
        url=f"https://api.digitalocean.com/v2/domains/{EXPECTED_DOMAIN}/records",
        match=[
            matchers.header_matcher(headers),
            matchers.query_param_matcher({"per_page": PAGE_RESULTS_LIMIT, "type": "A"}),
        ],
        status=404,
    )
    # Validate: Ensure that the HTTP error is bubbled up / not swallowed.
    with pytest.raises(requests.HTTPError, match=r"404"):
        subdomains.list_sub_domains(EXPECTED_DOMAIN)


class TestDomainNotManaged:
    """Domain is wholly unmanaged."""

    def test_unmanaged_A_records(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ):
        """Domain registered but not managed.

        Two A records registered for this domain.
        """
        EXPECTED_DOMAIN = "test.domain.example.com"
        EXPECTED_DOMAIN_RECORDS = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_A_records = mocker.patch.object(
            subdomains.do_api,
            "get_A_records",
            autospec=True,
        )
        mocked_get_A_records.return_value = EXPECTED_DOMAIN_RECORDS
        subdomains.list_sub_domains(EXPECTED_DOMAIN)

        mocked_get_A_records.assert_called_once_with(EXPECTED_DOMAIN)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {EXPECTED_DOMAIN}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {EXPECTED_DOMAIN}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " in captured_errout
        for record in EXPECTED_DOMAIN_RECORDS:
            assert record["name"] in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {EXPECTED_DOMAIN}" not in captured_errout

    def test_no_registered_A_records(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ):
        """Domain registered but not managed.

        Two A records registered for this domain.
        """
        EXPECTED_DOMAIN = "test.domain.example.com"
        EXPECTED_DOMAIN_RECORDS = []
        mocked_get_A_records = mocker.patch.object(
            subdomains.do_api,
            "get_A_records",
            autospec=True,
        )
        mocked_get_A_records.return_value = EXPECTED_DOMAIN_RECORDS
        subdomains.list_sub_domains(EXPECTED_DOMAIN)

        mocked_get_A_records.assert_called_once_with(EXPECTED_DOMAIN)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {EXPECTED_DOMAIN}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {EXPECTED_DOMAIN}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " not in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {EXPECTED_DOMAIN}" in captured_errout


class TestManagedDomain:
    """Top domain is managed; various states for subdomains/A records."""

    def test_no_A_records_registered(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ):
        """Domain managed, no A records registered."""
        EXPECTED_DOMAIN_RECORDS = []
        mocked_get_A_records = mocker.patch.object(
            subdomains.do_api,
            "get_A_records",
            autospec=True,
        )
        mocked_get_A_records.return_value = EXPECTED_DOMAIN_RECORDS
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_A_records.assert_called_once_with(added_top_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {added_top_domain}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " not in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" in captured_errout

    def test_only_unmanaged_A_records(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ):
        """A records exist, all are unmanaged."""
        EXPECTED_DOMAIN_RECORDS = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_A_records = mocker.patch.object(
            subdomains.do_api,
            "get_A_records",
            autospec=True,
        )
        mocked_get_A_records.return_value = EXPECTED_DOMAIN_RECORDS
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_A_records.assert_called_once_with(added_top_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {added_top_domain}" in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" not in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " in captured_errout
        for record in EXPECTED_DOMAIN_RECORDS:
            assert record["name"] in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" not in captured_errout

    def test_mix_managed_unmanaged_A_records(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
        mock_db_for_test: Connection,
    ):
        """One managed A record, One unmanaged A record."""
        EXPECTED_DOMAIN_RECORDS = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            # support is marked unmanaged and in the DB.
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
            # test is not in the DB at all
            {"id": 3, "name": "test", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_A_records = mocker.patch.object(
            subdomains.do_api,
            "get_A_records",
            autospec=True,
        )
        mocked_get_A_records.return_value = EXPECTED_DOMAIN_RECORDS

        # Arrange: Insert one of the domain records into the database.
        with mock_db_for_test:
            top_domain_id = mock_db_for_test.execute(
                "select id from domains where name = ?", (added_top_domain,)
            ).fetchone()["id"]
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
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
                    "domain_record_id": EXPECTED_DOMAIN_RECORDS[0]["id"],
                    "main_id": top_domain_id,
                    "name": EXPECTED_DOMAIN_RECORDS[0]["name"],
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
                    "domain_record_id": EXPECTED_DOMAIN_RECORDS[1]["id"],
                    "main_id": top_domain_id,
                    "name": EXPECTED_DOMAIN_RECORDS[1]["name"],
                    "current_ip4": "127.0.0.1",
                    "cataloged": now,
                    "last_checked": now,
                    "last_updated": now,
                },
            )

        # Test
        subdomains.list_sub_domains(added_top_domain)

        mocked_get_A_records.assert_called_once_with(added_top_domain)
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
        assert EXPECTED_DOMAIN_RECORDS[0]["name"] in managed_records_output

        # Report: unmanaged and registered A records
        assert EXPECTED_DOMAIN_RECORDS[1]["name"] in unmanaged_records_output
        assert EXPECTED_DOMAIN_RECORDS[2]["name"] in unmanaged_records_output

    def test_all_managed_A_records(
        self,
        added_top_domain: Literal["example.com"],
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
        mock_db_for_test: Connection,
    ):
        """All current A records are managed."""
        EXPECTED_DOMAIN_RECORDS = [
            {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
            {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
        ]
        mocked_get_A_records = mocker.patch.object(
            subdomains.do_api,
            "get_A_records",
            autospec=True,
        )
        mocked_get_A_records.return_value = EXPECTED_DOMAIN_RECORDS

        # Arrange: Insert all expected domain records into the database.
        with mock_db_for_test:
            top_domain_id = mock_db_for_test.execute(
                "select id from domains where name = ?", (added_top_domain,)
            ).fetchone()["id"]
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            for domain_record in EXPECTED_DOMAIN_RECORDS:
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

        mocked_get_A_records.assert_called_once_with(added_top_domain)
        captured_errout = capsys.readouterr().out

        # Report: no managed A records
        assert f"No managed A records for {added_top_domain}" not in captured_errout

        # Validate lack of output string: Do not report any managed A records
        assert f"Managed A records for {added_top_domain}" in captured_errout
        for record in EXPECTED_DOMAIN_RECORDS:
            assert record["name"] in captured_errout

        # Report: unmanaged and registered A records
        assert "Unmanaged A records for " not in captured_errout

        # Validate lack of output string: Do not report no unmanaged A records.
        assert f"No unmanaged A records for {added_top_domain}" in captured_errout
