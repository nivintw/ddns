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
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

from __future__ import annotations

import argparse
import textwrap

from ddns_digital_ocean import api_key_helpers, info, ip, logs

from . import domains


def configure_domains_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    """Configure the parser for the domains subparser"""
    parser_domains = subparsers.add_parser(name="domains", help="View and configure domains.")
    parser_domains.set_defaults(func=domains.main)

    group_domains = parser_domains.add_mutually_exclusive_group(required=True)
    group_domains.add_argument(
        "-l",
        "--list",
        help="List domains registered in your DigitalOcean account, indicating which are managed.",
        action="store_true",
    )

    group_domains.add_argument(
        "-a",
        "--add",
        help="Add <domain> to domains managed by ddns-digital-ocean.",
        metavar=("<domain>"),
    )


def configure_ip_lookup_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser_ip_server = subparsers.add_parser(
        name="ip_lookup_config",
        help=("Update the service/server used to lookup your public IP address."),
    )
    parser_ip_server.set_defaults(func=ip.view_or_update_ip_server)
    parser_ip_server.add_argument(
        "--url",
        help=(
            "The URL of the server to use for obtaining your current IP address. "
            "NOTE: Expects the servers response to a GET request to have a .text response. "
            "Example: https://api.ipify.org"
        ),
    )
    parser_ip_server.add_argument(
        "--ip-mode",
        choices=["4", "6"],
        default="4",
        help=("IPv4 or IPv6. Which IP address to update. Default: %(default)s"),
    )


def setup_argparse():
    parser = argparse.ArgumentParser(
        prog="do_ddns",
        description=textwrap.dedent(
            """
        Application to use domains from DigitalOcean account as dynamic DNS domain(s).
        The app only supports IP4. IPv6 is planned for a later release!

        You'll always find the latest version on https://github.com/nivintw/ddns
        For bugs, suggestions, pull requests visit https://github.com/nivintw/ddns/issues

        Forked with appreciation from https://gitlab.pm/rune/ddns
        """
        ).strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subparser_name")
    parser_update_ips = subparsers.add_parser(
        name="update_ips",
        help=("Update the IP addresses for the subdomains that are configured."),
    )
    parser_update_ips.set_defaults(func=ip.updateip)

    parser_update_ips.add_argument(
        "-f",
        "--force",
        help="Force update of IP address for all domains.",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    parser_logs = subparsers.add_parser(
        name="logs",
        help=("Print the logs."),
    )
    parser_logs.set_defaults(func=logs.show_log)
    parser_show_info = subparsers.add_parser(
        name="show_info",
        help="Show information about do_ddns, including current configuration and version.",
    )
    parser_show_info.set_defaults(func=info.show_current_info)
    parser_show_info.add_argument(
        "--show-api-key",
        help="Display the unmasked API key in output.",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    configure_domains_subparser(subparsers)
    configure_ip_lookup_subparser(subparsers)

    parser.add_argument(
        "-l",
        "--list",
        help="List subdomains for <domain> which are managed by ddns-digital-ocean.",
        nargs=1,
        metavar=("domain"),
        action="append",
    )

    parser.add_argument(
        "-u",
        "--show-unmanaged",
        help="List subdomains for <domain> which are not managed by ddns-digital-ocean.",
        nargs=1,
        metavar=("domain"),
        action="append",
    )

    parser.add_argument(
        "-c",
        "--current",
        help="List the current IP address for the sub-domain given",
        nargs=1,
        action="append",
    )

    parser.add_argument(
        "-s",
        "--sub",
        help=("Add new subdomain(s) to your DigitalOcean account and use as dynamic DNS."),
        nargs="+",
        metavar=("domain"),
    )

    parser.add_argument(
        "-k",
        "--local",
        help=("Add an existing DigitalOcean subdomain to your ddns DB and use as dynamic DNS."),
        nargs=2,
        metavar=("domain", "domainid"),
        action="append",
    )

    parser.add_argument(
        "-r",
        "--remove",
        help="Remove a subdomain from your DigitalOcean account and ddns.",
        nargs="+",
        metavar=("domain"),
    )

    parser.add_argument(
        "-e",
        "--edit",
        help="Changes domain from active to inactive or the other way around...",
        nargs=1,
        metavar=("test.example.com"),
        action="append",
    )

    parser_api_key = subparsers.add_parser(
        name="api_key",
        help="Add/Change the Digital Ocean API Key.",
    )
    parser_api_key.set_defaults(func=api_key_helpers.view_or_update)
    parser_api_key.add_argument(
        "-k",
        "--api-key-value",
        help="The API key value",
        type=str,
    )

    return parser
