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

from sqlite3 import Connection
from unittest.mock import call

import pytest
from pytest import CaptureFixture
from pytest_mock import MockerFixture

from ddns_digital_ocean import args, ip, subdomains

# Fixtures all tests in this module will use.
pytestmark = pytest.mark.usefixtures("mock_db_for_test")


@pytest.mark.usefixtures("mocked_responses")
class TestUpdateAllManagedSubdomains:
    """Update A records for all managed subdomains."""

    # TODO: Add checks for last_updated and last_checked values.

    def test_no_configured_subdomains(
        self,
    ):
        """No subdomains at all configured."""
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])

        with pytest.raises(subdomains.NoManagedSubdomainsError):
            test_args.func(test_args)

    def test_no_currently_managed_subdomains(
        self,
        mock_db_for_test,
        added_top_domain,
        mocker: MockerFixture,
    ):
        """Subdomains exist, but are marked unmanaged."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        EXPECTED_SUBDOMAINS = [
            "@",
            "support",
        ]
        EXPECTED_DOMAIN_RECORD_IDS = [
            10_001,
            10_002,
        ]
        EXPECTED_IP_ADDRESS = "127.0.0.1"

        mocked_create_A_record = mocker.patch.object(
            subdomains.do_api, "create_A_record", autospec=True
        )
        mocked_create_A_record.side_effect = EXPECTED_DOMAIN_RECORD_IDS
        # Arrange: Mock get_A_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record_by_name",
            autospec=True,
        )
        mocked_get_A_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (1.2): mark the subdomains as unmanaged.
        with mock_db_for_test:
            mock_db_for_test.execute(
                "update subdomains set managed = 0 where domain_record_id in (?, ?)",
                EXPECTED_DOMAIN_RECORD_IDS,
            )

        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])
        with pytest.raises(subdomains.NoManagedSubdomainsError):
            test_args.func(test_args)

    def test_all_current(
        self,
        added_top_domain,
        mocker: MockerFixture,
        capsys: CaptureFixture[str],
    ):
        """All managed subdomains have current IPs."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        EXPECTED_SUBDOMAINS = [
            "@",
            "support",
        ]
        EXPECTED_DOMAIN_RECORD_IDS = [
            10_001,
            10_002,
        ]
        EXPECTED_IP_ADDRESS = "127.0.0.1"

        from ddns_digital_ocean import subdomains

        mocked_create_A_record = mocker.patch.object(
            subdomains.do_api, "create_A_record", autospec=True
        )
        mocked_create_A_record.side_effect = EXPECTED_DOMAIN_RECORD_IDS
        # Arrange: Mock get_A_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record_by_name",
            autospec=True,
        )
        mocked_get_A_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        mocked_get_ip = mocker.patch.object(ip, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was not called.
        mocked_update_A_record = mocker.patch.object(
            subdomains.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines the IPs are current and don't need updating.

        # We expect this because all subdomains are marked as unmanaged.
        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record",
            autospec=True,
        )
        mocked_get_A_record.side_effect = [
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[0],
                "type": "A",
                "data": EXPECTED_IP_ADDRESS,
            },
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[1],
                "type": "A",
                "data": EXPECTED_IP_ADDRESS,
            },
        ]

        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])
        test_args.func(test_args)

        cap_errout = capsys.readouterr()

        # Validate: No errors occurred.
        # Validate: Reported "No updates necessary"
        assert "No updates necessary" in cap_errout.out

        # Validate that calls were made to check the current A record values.
        mocked_get_A_record.assert_has_calls(
            [
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
                    domain=added_top_domain,
                ),
            ]
        )
        # Validate: update_A_record function was not called.
        mocked_update_A_record.assert_not_called()

    def test_partial_update(
        self,
        added_top_domain,
        mocker: MockerFixture,
        capsys: CaptureFixture[str],
        mock_db_for_test: Connection,
    ):
        """Some configured subdomains need update."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        EXPECTED_SUBDOMAINS = [
            "@",
            "support",
        ]
        EXPECTED_DOMAIN_RECORD_IDS = [
            10_001,
            10_002,
        ]
        EXPECTED_IP_ADDRESS = "127.0.0.1"

        from ddns_digital_ocean import subdomains

        mocked_create_A_record = mocker.patch.object(
            subdomains.do_api, "create_A_record", autospec=True
        )
        mocked_create_A_record.side_effect = EXPECTED_DOMAIN_RECORD_IDS
        # Arrange: Mock get_A_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record_by_name",
            autospec=True,
        )
        mocked_get_A_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: This specific mock ensures that the "current ip" is "wrong"
        # before we call the update ip function.
        mocked_get_ip.side_effect = [
            "127.0.0.2",  # initial IP values; manage subdomain 1.
            "127.0.0.2",  # initial IP values; manage subdomain 2.
            EXPECTED_IP_ADDRESS,  # Update all managed subdomains get_ip() call.
        ]

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was called.
        mocked_update_A_record = mocker.patch.object(
            subdomains.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines that one of the IP addresses needs
        #   to be updated.

        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record",
            autospec=True,
        )
        mocked_get_A_record.side_effect = [
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[0],
                "type": "A",
                "data": EXPECTED_IP_ADDRESS,
            },
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[1],
                "type": "A",
                # NOTE: data != EXPECTED_IP_ADDRESS
                "data": "127.0.0.2",
            },
        ]

        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])
        test_args.func(test_args)

        cap_errout = capsys.readouterr()

        # Validate: No errors occurred.
        # Validate: Reported "Updates done."
        assert "Updates done." in cap_errout.out

        # Validate that calls were made to check the current A record values.
        mocked_get_A_record.assert_has_calls(
            [
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
                    domain=added_top_domain,
                ),
            ]
        )
        # Validate: update_A_record function was called once for
        # the second subdomain
        mocked_update_A_record.assert_called_once_with(
            domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
            domain=added_top_domain,
            new_ip_address=EXPECTED_IP_ADDRESS,
        )

        # Validate that the DB was updated.
        row = mock_db_for_test.execute(
            "select current_ip4 from subdomains where domain_record_id = 10001"
        ).fetchone()
        # NOTE: this seems odd/wrong, but is intentional.
        # We intentionally injected the below ip when first managing the subdomains.
        # We then created a situation where the DO domain records IP matched the "current" ip.
        # Thus, if the DB was updated correct, this particular row should still have the "bad" ip
        # of 127.0.0.2.
        # NOTE: if we change how we check for the update status / requirement,
        #   we'll need to revisit.
        assert row["current_ip4"] == "127.0.0.2"

        row = mock_db_for_test.execute(
            "select current_ip4 from subdomains where domain_record_id = 10002"
        ).fetchone()
        assert row["current_ip4"] == EXPECTED_IP_ADDRESS

    def test_all_need_update(
        self,
        added_top_domain,
        mock_db_for_test: Connection,
        mocker: MockerFixture,
        capsys: CaptureFixture[str],
    ):
        """All configured subdomains need update."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        EXPECTED_SUBDOMAINS = [
            "@",
            "support",
        ]
        EXPECTED_DOMAIN_RECORD_IDS = [
            10_001,
            10_002,
        ]
        EXPECTED_IP_ADDRESS = "127.0.0.1"

        from ddns_digital_ocean import subdomains

        mocked_create_A_record = mocker.patch.object(
            subdomains.do_api, "create_A_record", autospec=True
        )
        mocked_create_A_record.side_effect = EXPECTED_DOMAIN_RECORD_IDS
        # Arrange: Mock get_A_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record_by_name",
            autospec=True,
        )
        mocked_get_A_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: This specific mock ensures that the "current ip" is "wrong"
        # before we call the update ip function.
        mocked_get_ip.side_effect = [
            "127.0.0.2",  # initial IP values; manage subdomain 1.
            "127.0.0.2",  # initial IP values; manage subdomain 2.
            EXPECTED_IP_ADDRESS,  # Update all managed subdomains get_ip() call.
        ]

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was called.
        mocked_update_A_record = mocker.patch.object(
            subdomains.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines that all of the IP addresses need
        #   to be updated.

        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record",
            autospec=True,
        )
        mocked_get_A_record.side_effect = [
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[0],
                "type": "A",
                # NOTE: data != EXPECTED_IP_ADDRESS
                "data": "127.0.0.2",
            },
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[1],
                "type": "A",
                # NOTE: data != EXPECTED_IP_ADDRESS
                "data": "127.0.0.2",
            },
        ]

        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])
        test_args.func(test_args)

        cap_errout = capsys.readouterr()

        # Validate: No errors occurred.
        # Validate: Reported "Updates done."
        assert "Updates done." in cap_errout.out

        # Validate that calls were made to check the current A record values.
        mocked_get_A_record.assert_has_calls(
            [
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
                    domain=added_top_domain,
                ),
            ]
        )
        # Validate: update_A_record function was called for
        # both subdomains
        mocked_update_A_record.assert_has_calls(
            [
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[0],
                    domain=added_top_domain,
                    new_ip_address=EXPECTED_IP_ADDRESS,
                ),
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
                    domain=added_top_domain,
                    new_ip_address=EXPECTED_IP_ADDRESS,
                ),
            ]
        )

        # Validate that the DB was updated.
        rows = mock_db_for_test.execute("select current_ip4 from subdomains").fetchall()

        assert len(rows) != 0
        for subdomain in rows:
            assert subdomain["current_ip4"] == EXPECTED_IP_ADDRESS

    def test_force_update(
        self,
        added_top_domain,
        mock_db_for_test: Connection,
        mocker: MockerFixture,
        capsys: CaptureFixture[str],
    ):
        """The --force flag can be used to force an update, even when all are current."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        EXPECTED_SUBDOMAINS = [
            "@",
            "support",
        ]
        EXPECTED_DOMAIN_RECORD_IDS = [
            10_001,
            10_002,
        ]
        EXPECTED_IP_ADDRESS = "127.0.0.1"

        from ddns_digital_ocean import subdomains

        mocked_create_A_record = mocker.patch.object(
            subdomains.do_api, "create_A_record", autospec=True
        )
        mocked_create_A_record.side_effect = EXPECTED_DOMAIN_RECORD_IDS
        # Arrange: Mock get_A_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record_by_name",
            autospec=True,
        )
        mocked_get_A_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: intentionally "lying" about the current IP when first managing
        # the subdomains so that we can ensure the DB is updated.
        mocked_get_ip.side_effect = [
            "127.0.0.2",  # initial IP values; manage subdomain 1.
            "127.0.0.2",  # initial IP values; manage subdomain 2.
            EXPECTED_IP_ADDRESS,  # Update all managed subdomains get_ip() call.
        ]

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was not called.
        mocked_update_A_record = mocker.patch.object(
            subdomains.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines the IPs are current and don't need updating.

        mocked_get_A_record = mocker.patch.object(
            subdomains.do_api,
            "get_A_record",
            autospec=True,
        )
        mocked_get_A_record.side_effect = [
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[0],
                "type": "A",
                "data": EXPECTED_IP_ADDRESS,
            },
            {
                "id": EXPECTED_DOMAIN_RECORD_IDS[1],
                "type": "A",
                "data": EXPECTED_IP_ADDRESS,
            },
        ]

        parser = args.setup_argparse()
        # NOTE: Use --force flag to force updates, even though
        # we've configured things so that the IP addresses are current.
        test_args = parser.parse_args(args=["update-ips", "--force"])
        test_args.func(test_args)

        cap_errout = capsys.readouterr()

        # Validate: No errors occurred.
        # Validate: Reported "Updates done."
        assert "Updates done." in cap_errout.out

        # Validate that calls were made to check the current A record values.
        mocked_get_A_record.assert_has_calls(
            [
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
                    domain=added_top_domain,
                ),
            ]
        )

        # Validate: update_A_record function was called for
        # both subdomains
        mocked_update_A_record.assert_has_calls(
            [
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[0],
                    domain=added_top_domain,
                    new_ip_address=EXPECTED_IP_ADDRESS,
                ),
                call(
                    domain_record_id=EXPECTED_DOMAIN_RECORD_IDS[1],
                    domain=added_top_domain,
                    new_ip_address=EXPECTED_IP_ADDRESS,
                ),
            ]
        )

        # Validate that the DB was updated.
        rows = mock_db_for_test.execute("select current_ip4 from subdomains").fetchall()
        assert len(rows) != 0
        for subdomain in rows:
            assert subdomain["current_ip4"] == EXPECTED_IP_ADDRESS
