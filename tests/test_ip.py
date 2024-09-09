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

"""Tests for functions in the ip module."""

from sqlite3 import Connection
from unittest.mock import call

import pytest
import requests
from pytest import CaptureFixture
from pytest_mock import MockerFixture
from responses import RequestsMock

from ddns_digital_ocean import args, ip

# Fixtures all tests in this module will use.
pytestmark = pytest.mark.usefixtures("mock_db_for_test")


class TestConfigIPServer:
    def test_no_upstream_configured(
        self,
        mock_db_for_test: Connection,
    ):
        """We can configure the IP server when no prior IP server has been set."""
        EXPECTED_IP_SERVER = "https://iplookup.example.com"

        ip.config_ip_server(ipserver=EXPECTED_IP_SERVER, ip_type="4")

        # Validate: the ipserver for ipv4 has been configured.
        rows = mock_db_for_test.execute("select * from ipservers").fetchall()
        assert len(rows) == 1
        row = rows[0]

        assert row is not None
        assert row["URL"] == EXPECTED_IP_SERVER
        assert row["ip_version"] == "4"
        # NOTE: time now, we only support one single row/ip server config.
        assert row["id"] == 1

    def test_update_ip_server(
        self,
        mock_db_for_test: Connection,
    ):
        """We can update the IP server configuration."""
        EXPECTED_PRE_IP_SERVER = "https://iplookup.example.com"
        EXPECTED_POST_IP_SERVER = "https://new.iplookup.example.com"

        ip.config_ip_server(ipserver=EXPECTED_PRE_IP_SERVER, ip_type="4")
        ip.config_ip_server(ipserver=EXPECTED_POST_IP_SERVER, ip_type="4")

        # Validate: the ipserver for ipv4 has been configured.
        rows = mock_db_for_test.execute("select * from ipservers").fetchall()
        assert len(rows) == 1
        row = rows[0]

        assert row is not None
        assert row["URL"] == EXPECTED_POST_IP_SERVER
        assert row["ip_version"] == "4"
        # NOTE: time now, we only support one single row/ip server config.
        assert row["id"] == 1

    def test_ip_6_not_supported(
        self,
    ):
        """ipv6 is not supported."""
        EXPECTED_PRE_IP_SERVER = "https://iplookup.example.com"

        with pytest.raises(ip.IPv6NotSupportedError):
            ip.config_ip_server(ipserver=EXPECTED_PRE_IP_SERVER, ip_type="6")


class TestGetIP:
    def test_no_upstream_ip_resolver(
        self,
    ):
        """Inform user and raise NoIPResolverServerError when no upstream IP server configured."""
        with pytest.raises(ip.NoIPResolverServerError):
            ip.get_ip()

    def test_http_error_in_ip_lookup(
        self,
        mocked_responses: RequestsMock,
    ):
        """Raise any HTTP errors that occurred when calling ip resolver."""
        # Arrange
        EXPECTED_IP_SERVER = "https://iplookup.example.com"
        ip.config_ip_server(ipserver=EXPECTED_IP_SERVER, ip_type="4")

        mocked_responses.get(
            url=EXPECTED_IP_SERVER,
            body="",
            status=500,
        )

        # Test & Validate
        with pytest.raises(requests.exceptions.HTTPError):
            _ = ip.get_ip()

    def test_return_public_ip(
        self,
        mocked_responses: RequestsMock,
    ):
        """If configured correctly, return the current public IP4 address.
        NOTE: IP6 is not currently supported.
        """
        # Arrange
        EXPECTED_IP_SERVER = "https://iplookup.example.com"
        EXPECTED_IP = "127.0.0.1"
        ip.config_ip_server(ipserver=EXPECTED_IP_SERVER, ip_type="4")
        mocked_responses.get(
            url=EXPECTED_IP_SERVER,
            body=EXPECTED_IP,
        )

        # Test
        found_ip = ip.get_ip()

        # Validate
        assert found_ip == EXPECTED_IP


class TestViewUpdateIPServer:
    """function: view_or_update_ip_server with no config params set (view only)."""

    def test_output_no_config(
        self,
        capsys: CaptureFixture[str],
        mocker: MockerFixture,
    ):
        """Validate user output with no ip server configured"""
        spy_config_ip_server = mocker.spy(ip, "config_ip_server")

        parser = args.setup_argparse()
        # NOTE: intentionally don't supply any args
        #  in order to force the "view" mode.
        test_args = parser.parse_args(args=["ip_lookup_config"])

        ip.view_or_update_ip_server(test_args)

        # Validate that the ip server is not configured.
        # This is based on how we're calling view_our_update_ip_server.
        spy_config_ip_server.assert_not_called()

        capd_err_out = capsys.readouterr()
        assert "IP v4 resolver  : None Configured" in capd_err_out.out

    def test_output_ip_server_configured(
        self,
        capsys: CaptureFixture[str],
        mocker: MockerFixture,
    ):
        """Test output with ipv4 server configured"""
        # Arrange
        EXPECTED_IP_SERVER = "https://iplookup.example.com"
        ip.config_ip_server(ipserver=EXPECTED_IP_SERVER, ip_type="4")

        # Arrange: spy config_ip_server AFTER we call it
        #   so we can ensure it is not called again.
        spy_config_ip_server = mocker.spy(ip, "config_ip_server")

        parser = args.setup_argparse()
        # NOTE: intentionally don't supply any args
        #  in order to force the "view" mode.
        test_args = parser.parse_args(args=["ip_lookup_config"])

        ip.view_or_update_ip_server(test_args)

        # Validate that the ip server is not configured.
        # This is based on how we're calling view_our_update_ip_server.
        spy_config_ip_server.assert_not_called()

        capd_err_out = capsys.readouterr()
        assert f"IP v4 resolver  : {EXPECTED_IP_SERVER}" in capd_err_out.out

    def test_config_and_output_ip_server(
        self,
        capsys: CaptureFixture[str],
        mocker: MockerFixture,
    ):
        """When called with args.url, configure the IP server before showing config."""
        # Arrange
        EXPECTED_IP_SERVER = "https://config.iplookup.example.com"
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["ip_lookup_config", "--url", EXPECTED_IP_SERVER])
        spy_config_ip_server = mocker.spy(ip, "config_ip_server")

        ip.view_or_update_ip_server(test_args)

        spy_config_ip_server.assert_called_once_with(test_args.url, test_args.ip_mode)

        capd_err_out = capsys.readouterr()
        assert f"IP v4 resolver  : {EXPECTED_IP_SERVER}" in capd_err_out.out


@pytest.fixture()
def added_top_domain(
    mock_db_for_test: Connection,
    mocker: MockerFixture,
):
    """Inject a top-level domain into the test DB."""
    from ddns_digital_ocean import domains

    EXPECTED_TOP_DOMAIN = "example.com"
    mocked_verify_domain_registered = mocker.patch.object(
        domains.do_api, "verify_domain_is_registered", autospec=True
    )

    domains.manage_domain(EXPECTED_TOP_DOMAIN)

    yield EXPECTED_TOP_DOMAIN
    mocked_verify_domain_registered.assert_called_once_with(EXPECTED_TOP_DOMAIN)


@pytest.mark.usefixtures("mocked_responses", "mock_db_for_test")
class TestUpdateAllManagedSubdomains:
    """Update A records for all managed subdomains."""

    # TODO: Add checks for last_updated and last_checked values.

    def test_no_configured_subdomains(
        self,
    ):
        """No subdomains at all configured."""
        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update_ips"])

        with pytest.raises(ip.NoConfiguredSubdomainsError):
            ip.update_all_managed_subdomains(test_args)

    def test_no_currently_managed_subdomains(
        self,
        mock_db_for_test,
        added_top_domain,
        mocker: MockerFixture,
        capsys: CaptureFixture[str],
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

        from ddns_digital_ocean import subdomains

        mocked_create_A_record = mocker.patch.object(
            subdomains.do_api, "create_A_record", autospec=True
        )
        mocked_create_A_record.side_effect = EXPECTED_DOMAIN_RECORD_IDS

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        mocked_get_ip = mocker.patch.object(ip, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (1.2): mark the subdomains as unmanaged.
        with mock_db_for_test:
            mock_db_for_test.execute(
                "update subdomains set managed = 0 " "where domain_record_id in (?, ?)",
                EXPECTED_DOMAIN_RECORD_IDS,
            )
        # Arrange (2): Mock the update_A_record method
        # so we assert that it was not called.
        mocked_update_A_record = mocker.patch.object(
            ip.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can assert that it was not called.
        # We expect this because all subdomains are marked as unmanaged.
        mocked_get_A_record = mocker.patch.object(
            ip.do_api,
            "get_A_record",
            autospec=True,
        )

        parser = args.setup_argparse()
        test_args = parser.parse_args(args=["update_ips"])
        ip.update_all_managed_subdomains(test_args)

        cap_errout = capsys.readouterr()

        # Validate: No errors occurred.
        # Validate: Reported "No updates necessary"
        assert "No updates necessary" in cap_errout.out
        # Validate: *_A_record functions not called.
        mocked_update_A_record.assert_not_called()
        mocked_get_A_record.assert_not_called()

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
            ip.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines the IPs are current and don't need updating.

        # We expect this because all subdomains are marked as unmanaged.
        mocked_get_A_record = mocker.patch.object(
            ip.do_api,
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
        test_args = parser.parse_args(args=["update_ips"])
        ip.update_all_managed_subdomains(test_args)

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

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: This specific mock ensures that the "current ip" is "wrong"
        # before we call the update ip function.
        mocked_get_ip.return_value = "127.0.0.2"

        mocked_get_ip = mocker.patch.object(ip, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was called.
        mocked_update_A_record = mocker.patch.object(
            ip.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines that one of the IP addresses needs
        #   to be updated.

        mocked_get_A_record = mocker.patch.object(
            ip.do_api,
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
        test_args = parser.parse_args(args=["update_ips"])
        ip.update_all_managed_subdomains(test_args)

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

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: This specific mock ensures that the "current ip" is "wrong"
        # before we call the update ip function.
        mocked_get_ip.return_value = "127.0.0.2"

        mocked_get_ip = mocker.patch.object(ip, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was called.
        mocked_update_A_record = mocker.patch.object(
            ip.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines that all of the IP addresses need
        #   to be updated.

        mocked_get_A_record = mocker.patch.object(
            ip.do_api,
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
        test_args = parser.parse_args(args=["update_ips"])
        ip.update_all_managed_subdomains(test_args)

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

        # Arrange (1.1): Mock out calls to get_ip.
        mocked_get_ip = mocker.patch.object(subdomains, "get_ip", autospec=True)
        # NOTE: intentionally "lying" about the current IP when first managing
        # the subdomains so that we can ensure the DB is updated.
        mocked_get_ip.return_value = "127.0.0.2"

        mocked_get_ip = mocker.patch.object(ip, "get_ip", autospec=True)
        mocked_get_ip.return_value = EXPECTED_IP_ADDRESS

        for subdomain in EXPECTED_SUBDOMAINS:
            subdomains.manage_subdomain(subdomain, added_top_domain)

        # Arrange (2): Mock the update_A_record method
        # so we assert that it was not called.
        mocked_update_A_record = mocker.patch.object(
            ip.do_api,
            "update_A_record",
            autospec=True,
        )
        # Arrange (3): Mock the get_A_record method
        # so we can configure it's return values.
        # NOTE: This is how we create the situation under test.
        # i.e. this is what determines the IPs are current and don't need updating.

        mocked_get_A_record = mocker.patch.object(
            ip.do_api,
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
        test_args = parser.parse_args(args=["update_ips", "--force"])
        ip.update_all_managed_subdomains(test_args)

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
