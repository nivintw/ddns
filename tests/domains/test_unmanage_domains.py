# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for the un_manage_domain function."""

import datetime as dt
from sqlite3 import Connection

import pytest

from digital_ocean_dynamic_dns import domains


@pytest.mark.usefixtures("mock_db_for_test", "mocked_responses", "preload_api_key")
class TestUnManageDomain:
    """Tests for the un_manage_domain function."""

    def test_domain_not_in_db(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Call unmanage_domain with a domain not in database."""
        expected_domain = "sentinel.new.test.domain.local"

        domains.un_manage_domain(expected_domain)

        # Validate: Ensure user was informed.
        captured_output = capsys.readouterr().out
        captured_output = " ".join(captured_output.split())
        assert (
            f"The domain {expected_domain} is not managed by digital-ocean-dynamic-dns."
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
    ) -> None:
        """All sub-domains and the top-level domain are marked un-managed."""
        expected_domain = "sentinel.existing.test.domain.local"
        expected_ip4_address = "127.0.0.1"

        # Arrange: inject the domain directly into the table before
        # calling the function under test.
        with mock_db_for_test:
            update_datetime = dt.datetime.now(tz=dt.UTC).astimezone().strftime("%Y-%m-%d %H:%M")
            mock_db_for_test.execute(
                "INSERT INTO domains(name, cataloged, last_managed) "
                " values(:name, :cataloged, :last_managed)",
                {
                    "name": expected_domain,
                    "cataloged": update_datetime,
                    "last_managed": update_datetime,
                },
            )
            for i, subdomain in enumerate(subdomains):
                # Arrange: Insert expected_subdomain into the db
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
                        "current_ip4": expected_ip4_address,
                        "cataloged": update_datetime,
                        "last_checked": update_datetime,
                        "last_updated": update_datetime,
                        "managed": subdomain["managed"],
                    },
                )

        domains.un_manage_domain(expected_domain)

        # Ensure values were unchanged.
        with mock_db_for_test:
            row = mock_db_for_test.execute(
                "select * from domains where name = ?", (expected_domain,)
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
            f"Domain {expected_domain} is no longer managed. "
            f"{len([x for x in subdomains if x['managed'] == 1])} "
            "related subdomains also no longer managed."
        ) in capd_out
