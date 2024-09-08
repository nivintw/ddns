# ddns-digital-ocean
# Copyright (C) 2023  Tyler Nivin <tyler@nivin.tech>
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
from pytest_mock import MockerFixture

from ddns_digital_ocean import domains


@pytest.mark.usefixtures("mock_db_for_test", "mocked_responses", "preload_api_key")
class TestManageDomain:
    def test_manage_domain_empty_db(
        self,
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
    ):
        """Add a domain to an empty database as managed."""
        EXPECTED_NEW_DOMAIN = "sentinel.new.test.domain.local"

        # Arrange: Mock verify_domain_is_registered.
        # No return necessary; lack of exception being raised means success.
        mocked_verify_domain = mocker.patch.object(
            domains.do_api,
            "verify_domain_is_registered",
            autospec=True,
        )

        domains.manage_domain(EXPECTED_NEW_DOMAIN)

        # Validate that verify_domain_is_registered was called.
        mocked_verify_domain.assert_called_once_with(EXPECTED_NEW_DOMAIN)

        # Validate: Ensure domain was added to the database.
        with mock_db_for_test:
            cursor = mock_db_for_test.execute(
                "SELECT * FROM domains where name = ?", (EXPECTED_NEW_DOMAIN,)
            )
            row = cursor.fetchone()
            assert row["name"] == EXPECTED_NEW_DOMAIN
            assert row["id"] == 1
            assert dt.datetime.strptime(row["cataloged"], "%Y-%m-%d %H:%M") <= dt.datetime.now()
            assert dt.datetime.strptime(row["last_managed"], "%Y-%m-%d %H:%M") <= dt.datetime.now()

        # Validate: Ensure user was informed.
        captured_output = capsys.readouterr()
        assert f"The domain {EXPECTED_NEW_DOMAIN} has been added to the DB" in captured_output.out

    def test_manage_domain_already_in_db(
        self,
        mock_db_for_test: Connection,
    ):
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
        EXPECTED_EXISTING_DOMAIN = "sentinel.existing.test.domain.local"

        # Arrange: inject the domain directly into the table before
        # calling the function under test.
        with mock_db_for_test:
            update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
            mock_db_for_test.execute(
                "INSERT INTO domains(name, cataloged, last_managed) "
                " values(:name, :cataloged, :last_managed)",
                {
                    "name": EXPECTED_EXISTING_DOMAIN,
                    "cataloged": update_datetime,
                    "last_managed": update_datetime,
                },
            )

        domains.manage_domain(EXPECTED_EXISTING_DOMAIN)

        # Ensure values were unchanged.
        with mock_db_for_test:
            cursor = mock_db_for_test.execute(
                "select * from domains where name = ?", (EXPECTED_EXISTING_DOMAIN,)
            )
            row = cursor.fetchone()
            assert row["cataloged"] == update_datetime
            assert row["last_managed"] == update_datetime
