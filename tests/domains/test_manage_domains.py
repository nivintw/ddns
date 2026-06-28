# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for domain management functions."""

import datetime as dt
from sqlite3 import Connection
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import domains


@pytest.mark.usefixtures("mock_db_for_test", "mocked_responses", "preload_api_key")
class TestManageDomain:
    """Tests for the manage_domain function."""

    def test_manage_domain_empty_db(
        self,
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
    ) -> None:
        """Add a domain to an empty database as managed."""
        expected_new_domain = "sentinel.new.test.domain.local"

        # Arrange: Mock verify_domain_is_registered.
        # No return necessary; lack of exception being raised means success.
        mocked_verify_domain = mocker.patch.object(
            domains.do_api,
            "verify_domain_is_registered",
            autospec=True,
        )

        domains.manage_domain(expected_new_domain)

        # Validate that verify_domain_is_registered was called.
        mocked_verify_domain.assert_called_once_with(expected_new_domain)

        # Validate: Ensure domain was added to the database.
        with mock_db_for_test:
            cursor = mock_db_for_test.execute(
                "SELECT * FROM domains where name = ?", (expected_new_domain,)
            )
            row = cursor.fetchone()
            assert row["name"] == expected_new_domain
            assert row["id"] == 1
            now = dt.datetime.now(tz=dt.UTC).astimezone()
            local_tz = now.tzinfo
            assert (
                dt.datetime.strptime(row["cataloged"], "%Y-%m-%d %H:%M").replace(tzinfo=local_tz)
                <= now
            )
            assert (
                dt.datetime.strptime(row["last_managed"], "%Y-%m-%d %H:%M").replace(tzinfo=local_tz)
                <= now
            )

        # Validate: Ensure user was informed.
        captured_output = capsys.readouterr()
        assert f"The domain {expected_new_domain} has been added to the DB" in captured_output.out

    def test_manage_domain_already_in_db(
        self,
        mock_db_for_test: Connection,
    ) -> None:
        """If user tries to add a DB already in the database we change nothing.

        This is not an error state.

        Note: I don't configure any mocked requests because,
          the way this test and the function under test are written,
          no http(s) requests should be made.

        Validates:
            1. No requests are made
                - If there were a request, it would mean we haven't early-exited
                    after checking the local db.
        """
        expected_existing_domain = "sentinel.existing.test.domain.local"

        # Arrange: inject the domain directly into the table before
        # calling the function under test.
        with mock_db_for_test:
            update_datetime = dt.datetime.now(tz=dt.UTC).astimezone().strftime("%Y-%m-%d %H:%M")
            mock_db_for_test.execute(
                "INSERT INTO domains(name, cataloged, last_managed) "
                " values(:name, :cataloged, :last_managed)",
                {
                    "name": expected_existing_domain,
                    "cataloged": update_datetime,
                    "last_managed": update_datetime,
                },
            )

        domains.manage_domain(expected_existing_domain)

        # Ensure values were unchanged.
        with mock_db_for_test:
            cursor = mock_db_for_test.execute(
                "select * from domains where name = ?", (expected_existing_domain,)
            )
            row = cursor.fetchone()
            assert row["cataloged"] == update_datetime
            assert row["last_managed"] == update_datetime


@pytest.mark.parametrize(
    "existing_a_records",
    [
        pytest.param([], id="no-a-records"),
        pytest.param(
            [
                {"id": 1, "name": "@", "data": "127.0.0.1", "ttl": 1800},
                {"id": 2, "name": "support", "data": "127.0.0.1", "ttl": 1800},
            ],
            id="two-a-records",
        ),
    ],
)
def test_manage_all_existing_a_records(
    existing_a_records: list,
    mocker: MockerFixture,
) -> None:
    """We can manage all existing A records for a given domain."""
    expected_domain = "example.com"

    mocked_get_a_records = mocker.patch.object(domains.do_api, "get_a_records", autospec=True)
    mocked_get_a_records.return_value = existing_a_records

    mocked_managed_subdomain = mocker.patch.object(domains, "manage_subdomain", autospec=True)

    domains.manage_all_existing_a_records(expected_domain)

    mocked_get_a_records.assert_called_once_with(expected_domain)

    if not existing_a_records:
        mocked_managed_subdomain.assert_not_called()
    else:
        mocked_managed_subdomain.assert_has_calls(
            [call(subdomain=x["name"], domain=expected_domain) for x in existing_a_records]
        )
