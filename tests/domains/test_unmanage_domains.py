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

from ddns_digital_ocean import domains


@pytest.mark.usefixtures("mock_db_for_test", "mocked_responses", "preload_api_key")
class TestUnManageDomain:
    def test_domain_not_in_db(
        self,
        capsys: pytest.CaptureFixture[str],
    ):
        """Call unmanage_domain with a domain not in database."""
        EXPECTED_DOMAIN = "sentinel.new.test.domain.local"

        domains.un_manage_domain(EXPECTED_DOMAIN)

        # Validate: Ensure user was informed.
        captured_output = capsys.readouterr().out
        captured_output = " ".join(captured_output.split())
        assert (
            f"The domain {EXPECTED_DOMAIN} is not managed by digital-ocean-dynamic-dns."
            in captured_output
        )

    @pytest.mark.parametrize(
        "subdomains",
        [
            pytest.param([], id="no-managed-subs"),
            pytest.param(
                [{"name": "@", "managed": 1}, {"name": "support", "managed": 1}],
                id="all-managed-subs",
            ),
            pytest.param(
                [{"name": "@", "managed": 1}, {"name": "support", "managed": 0}],
                id="mixed-subs",
            ),
        ],
    )
    def test_side_effects(
        self,
        mock_db_for_test: Connection,
        subdomains: list[dict],
        capsys: pytest.CaptureFixture[str],
    ):
        """All sub-domains and the top-level domain are marked un-managed."""
        EXPECTED_DOMAIN = "sentinel.existing.test.domain.local"
        EXPECTED_IP4_ADDRESS = "127.0.0.1"

        # Arrange: inject the domain directly into the table before
        # calling the function under test.
        with mock_db_for_test:
            update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
            mock_db_for_test.execute(
                "INSERT INTO domains(name, cataloged, last_managed) "
                " values(:name, :cataloged, :last_managed)",
                {
                    "name": EXPECTED_DOMAIN,
                    "cataloged": update_datetime,
                    "last_managed": update_datetime,
                },
            )
            for i, subdomain in enumerate(subdomains):
                # Arrange: Insert EXPECTED_SUBDOMAIN into the db
                # as a managed subdomain.
                mock_db_for_test.execute(
                    "INSERT INTO subdomains("
                    "   domain_record_id,"
                    "   main_id,"
                    "   name,"
                    "   current_ip4,"
                    "   cataloged,"
                    "   last_checked,"
                    "   last_updated,"
                    "   managed"
                    ") values("
                    "   :domain_record_id,"
                    "   :main_id,"
                    "   :name,"
                    "   :current_ip4,"
                    "   :cataloged,"
                    "   :last_checked,"
                    "   :last_updated,"
                    "   :managed"
                    ")",
                    {
                        "domain_record_id": i,
                        "main_id": 1,  # expected id from domains.id
                        "name": subdomain["name"],
                        "current_ip4": EXPECTED_IP4_ADDRESS,
                        "cataloged": update_datetime,
                        "last_checked": update_datetime,
                        "last_updated": update_datetime,
                        "managed": subdomain["managed"],
                    },
                )

        domains.un_manage_domain(EXPECTED_DOMAIN)

        # Ensure values were unchanged.
        with mock_db_for_test:
            row = mock_db_for_test.execute(
                "select * from domains where name = ?", (EXPECTED_DOMAIN,)
            ).fetchone()
            assert row["managed"] == 0

            rows = mock_db_for_test.execute(
                "select * from subdomains where main_id = ?", (row["id"],)
            ).fetchall()
            if subdomains:
                # Should be a non-empty list
                assert rows
            for row in rows:
                assert row["managed"] == 0

        # Validate user feedback.
        capd_out = " ".join(capsys.readouterr().out.split())
        assert (
            f"Domain {EXPECTED_DOMAIN} is no longer managed. "
            f"{len([ x for x in subdomains if x["managed"] == 1])} "
            "related subdomains also no longer managed."
        ) in capd_out
