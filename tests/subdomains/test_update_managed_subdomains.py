# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Tests for updating A records for all managed subdomains."""

from sqlite3 import Connection
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import args, ip, subdomains

# Fixtures all tests in this module will use.
pytestmark = pytest.mark.usefixtures("mock_db_for_test")


@pytest.mark.usefixtures("mocked_responses")
class TestUpdateAllManagedSubdomains:
    """Update A records for all managed subdomains."""

    def test_no_configured_subdomains(
        self,
    ) -> None:
        """No subdomains at all configured."""
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])

        with pytest.raises(subdomains.NoManagedSubdomainsError):
            test_args.func(test_args)

    def test_no_currently_managed_subdomains(
        self,
        mock_db_for_test: Connection,
        added_top_domain: str,
        mocker: MockerFixture,
    ) -> None:
        """Subdomains exist, but are marked unmanaged."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        expected_subdomains = [
            "@",
            "support",
        ]
        expected_domain_record_ids = [
            10_001,
            10_002,
        ]
        expected_ip_address = "127.0.0.1"

        mocked_create_a_record = mocker.patch.object(
            subdomains.do_api, "create_a_record", autospec=True
        )
        mocked_create_a_record.side_effect = expected_domain_record_ids
        # Arrange: Mock get_a_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record_by_name",
            autospec=True,
        )
        mocked_get_a_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        mocked_get_ip.return_value = expected_ip_address

        for subdomain in expected_subdomains:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (1.2): mark the subdomains as unmanaged.
        with mock_db_for_test:
            mock_db_for_test.execute(
                "update subdomains set managed = 0 where domain_record_id in (?, ?)",
                expected_domain_record_ids,
            )

        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update-ips"])
        with pytest.raises(subdomains.NoManagedSubdomainsError):
            test_args.func(test_args)

    def test_all_current(
        self,
        added_top_domain: str,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """All managed subdomains have current IPs."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        expected_subdomains = [
            "@",
            "support",
        ]
        expected_domain_record_ids = [
            10_001,
            10_002,
        ]
        expected_ip_address = "127.0.0.1"

        mocked_create_a_record = mocker.patch.object(
            subdomains.do_api, "create_a_record", autospec=True
        )
        mocked_create_a_record.side_effect = expected_domain_record_ids
        # Arrange: Mock get_a_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record_by_name",
            autospec=True,
        )
        mocked_get_a_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        mocked_get_ip.return_value = expected_ip_address

        mocked_get_ip = mocker.patch.object(ip, "get_ip", autospec=True)
        mocked_get_ip.return_value = expected_ip_address

        for subdomain in expected_subdomains:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_a_record method
        # so we assert that it was not called.
        mocked_update_a_record = mocker.patch.object(
            subdomains.do_api,
            "update_a_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_a_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines the IPs are current and don't need updating.

        # We expect this because all subdomains are marked as unmanaged.
        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record",
            autospec=True,
        )
        mocked_get_a_record.side_effect = [
            {
                "id": expected_domain_record_ids[0],
                "type": "A",
                "data": expected_ip_address,
            },
            {
                "id": expected_domain_record_ids[1],
                "type": "A",
                "data": expected_ip_address,
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
        mocked_get_a_record.assert_has_calls(
            [
                call(
                    domain_record_id=expected_domain_record_ids[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=expected_domain_record_ids[1],
                    domain=added_top_domain,
                ),
            ]
        )
        # Validate: update_a_record function was not called.
        mocked_update_a_record.assert_not_called()

    def test_partial_update(
        self,
        added_top_domain: str,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
        mock_db_for_test: Connection,
    ) -> None:
        """Some configured subdomains need update."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        expected_subdomains = [
            "@",
            "support",
        ]
        expected_domain_record_ids = [
            10_001,
            10_002,
        ]
        expected_ip_address = "127.0.0.1"

        mocked_create_a_record = mocker.patch.object(
            subdomains.do_api, "create_a_record", autospec=True
        )
        mocked_create_a_record.side_effect = expected_domain_record_ids
        # Arrange: Mock get_a_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record_by_name",
            autospec=True,
        )
        mocked_get_a_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: This specific mock ensures that the "current ip" is "wrong"
        # before we call the update ip function.
        mocked_get_ip.side_effect = [
            "127.0.0.2",  # initial IP values; manage subdomain 1.
            "127.0.0.2",  # initial IP values; manage subdomain 2.
            expected_ip_address,  # Update all managed subdomains get_ip() call.
        ]

        for subdomain in expected_subdomains:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_a_record method
        # so we assert that it was called.
        mocked_update_a_record = mocker.patch.object(
            subdomains.do_api,
            "update_a_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_a_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines that one of the IP addresses needs
        #   to be updated.

        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record",
            autospec=True,
        )
        mocked_get_a_record.side_effect = [
            {
                "id": expected_domain_record_ids[0],
                "type": "A",
                "data": expected_ip_address,
            },
            {
                "id": expected_domain_record_ids[1],
                "type": "A",
                # NOTE: data is intentionally stale (differs from expected_ip_address)
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
        mocked_get_a_record.assert_has_calls(
            [
                call(
                    domain_record_id=expected_domain_record_ids[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=expected_domain_record_ids[1],
                    domain=added_top_domain,
                ),
            ]
        )
        # Validate: update_a_record function was called once for
        # the second subdomain
        mocked_update_a_record.assert_called_once_with(
            domain_record_id=expected_domain_record_ids[1],
            domain=added_top_domain,
            new_ip_address=expected_ip_address,
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
        assert row["current_ip4"] == expected_ip_address

    def test_all_need_update(
        self,
        added_top_domain: str,
        mock_db_for_test: Connection,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """All configured subdomains need update."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        expected_subdomains = [
            "@",
            "support",
        ]
        expected_domain_record_ids = [
            10_001,
            10_002,
        ]
        expected_ip_address = "127.0.0.1"

        mocked_create_a_record = mocker.patch.object(
            subdomains.do_api, "create_a_record", autospec=True
        )
        mocked_create_a_record.side_effect = expected_domain_record_ids
        # Arrange: Mock get_a_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record_by_name",
            autospec=True,
        )
        mocked_get_a_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: This specific mock ensures that the "current ip" is "wrong"
        # before we call the update ip function.
        mocked_get_ip.side_effect = [
            "127.0.0.2",  # initial IP values; manage subdomain 1.
            "127.0.0.2",  # initial IP values; manage subdomain 2.
            expected_ip_address,  # Update all managed subdomains get_ip() call.
        ]

        for subdomain in expected_subdomains:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_a_record method
        # so we assert that it was called.
        mocked_update_a_record = mocker.patch.object(
            subdomains.do_api,
            "update_a_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_a_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines that all of the IP addresses need
        #   to be updated.

        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record",
            autospec=True,
        )
        mocked_get_a_record.side_effect = [
            {
                "id": expected_domain_record_ids[0],
                "type": "A",
                # NOTE: data is intentionally stale (differs from expected_ip_address)
                "data": "127.0.0.2",
            },
            {
                "id": expected_domain_record_ids[1],
                "type": "A",
                # NOTE: data is intentionally stale (differs from expected_ip_address)
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
        mocked_get_a_record.assert_has_calls(
            [
                call(
                    domain_record_id=expected_domain_record_ids[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=expected_domain_record_ids[1],
                    domain=added_top_domain,
                ),
            ]
        )
        # Validate: update_a_record function was called for
        # both subdomains
        mocked_update_a_record.assert_has_calls(
            [
                call(
                    domain_record_id=expected_domain_record_ids[0],
                    domain=added_top_domain,
                    new_ip_address=expected_ip_address,
                ),
                call(
                    domain_record_id=expected_domain_record_ids[1],
                    domain=added_top_domain,
                    new_ip_address=expected_ip_address,
                ),
            ]
        )

        # Validate that the DB was updated.
        rows = mock_db_for_test.execute("select current_ip4 from subdomains").fetchall()

        assert len(rows) != 0
        for subdomain in rows:
            assert subdomain["current_ip4"] == expected_ip_address

    def test_force_update(
        self,
        added_top_domain: str,
        mock_db_for_test: Connection,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The --force flag can be used to force an update, even when all are current."""
        # Arrange (1): Configure two subdomains, but marked unmanaged.
        expected_subdomains = [
            "@",
            "support",
        ]
        expected_domain_record_ids = [
            10_001,
            10_002,
        ]
        expected_ip_address = "127.0.0.1"

        mocked_create_a_record = mocker.patch.object(
            subdomains.do_api, "create_a_record", autospec=True
        )
        mocked_create_a_record.side_effect = expected_domain_record_ids
        # Arrange: Mock get_a_record_by_name so our dependent arrange steps
        # can manage the subdomains without needing to call out.
        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record_by_name",
            autospec=True,
        )
        mocked_get_a_record.return_value = []

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: intentionally "lying" about the current IP when first managing
        # the subdomains so that we can ensure the DB is updated.
        mocked_get_ip.side_effect = [
            "127.0.0.2",  # initial IP values; manage subdomain 1.
            "127.0.0.2",  # initial IP values; manage subdomain 2.
            expected_ip_address,  # Update all managed subdomains get_ip() call.
        ]

        for subdomain in expected_subdomains:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_a_record method
        # so we assert that it was not called.
        mocked_update_a_record = mocker.patch.object(
            subdomains.do_api,
            "update_a_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_a_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines the IPs are current and don't need updating.

        mocked_get_a_record = mocker.patch.object(
            subdomains.do_api,
            "get_a_record",
            autospec=True,
        )
        mocked_get_a_record.side_effect = [
            {
                "id": expected_domain_record_ids[0],
                "type": "A",
                "data": expected_ip_address,
            },
            {
                "id": expected_domain_record_ids[1],
                "type": "A",
                "data": expected_ip_address,
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
        mocked_get_a_record.assert_has_calls(
            [
                call(
                    domain_record_id=expected_domain_record_ids[0],
                    domain=added_top_domain,
                ),
                call(
                    domain_record_id=expected_domain_record_ids[1],
                    domain=added_top_domain,
                ),
            ]
        )

        # Validate: update_a_record function was called for
        # both subdomains
        mocked_update_a_record.assert_has_calls(
            [
                call(
                    domain_record_id=expected_domain_record_ids[0],
                    domain=added_top_domain,
                    new_ip_address=expected_ip_address,
                ),
                call(
                    domain_record_id=expected_domain_record_ids[1],
                    domain=added_top_domain,
                    new_ip_address=expected_ip_address,
                ),
            ]
        )

        # Validate that the DB was updated.
        rows = mock_db_for_test.execute("select current_ip4 from subdomains").fetchall()
        assert len(rows) != 0
        for subdomain in rows:
            assert subdomain["current_ip4"] == expected_ip_address
