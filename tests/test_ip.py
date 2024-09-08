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
