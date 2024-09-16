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

from __future__ import annotations

import argparse
import textwrap

from digital_ocean_dynamic_dns import info, ip, logs, manage, subdomains

from . import domains


def configure_ip_lookup_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser_ip_server = subparsers.add_parser(
        name="ip-resolver-config",
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


def configure_manage_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    """Subparser `manage`"""
    parser_manage = subparsers.add_parser(
        name="manage",
        help="Configure domains and subdomains to be managed by digital-ocean-dynamic-dns",
    )
    parser_manage.set_defaults(func=manage.martial_manage)
    parser_manage.add_argument(
        "domain",
        help=(
            "The domain for which A records will be created. "
            "If --subdomain is NOT specified, then all current A records for `domain` will be "
            "imported and managed moving forward. "
            "If --subdomain _is_ specified, then A records will only be managed for"
            " that --subdomain."
        ),
    )
    group_show_add = parser_manage.add_mutually_exclusive_group()
    group_show_add.add_argument(
        "--subdomain",
        help="The subdomain (i.e. `name` for the A record) to manage for `domain`",
    )
    group_show_add.add_argument(
        "--list",
        help="List the current subdomains (A records) for `domain`",
        action="store_true",
    )


def configure_un_manage_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    """subparser `un-manage`"""
    parser = subparsers.add_parser(
        name="un-manage",
        help="Stop digital-ocean-dynamic-dns from managing the specified domains and subdomains.",
    )
    parser.set_defaults(func=manage.martial_un_manage)
    parser.add_argument(
        "domain",
        help=(
            "The domain for which A records are managed. "
            "If --subdomain is NOT specified, then all currently managed A records "
            "for `domain` will stop being managed."
            "If --subdomain _is_ specified, then only A records for --subdomain"
            " will stop being managed."
        ),
    )
    group_show_add = parser.add_mutually_exclusive_group()
    group_show_add.add_argument(
        "--subdomain",
        help="The subdomain (i.e. `name` for the A record) to stop managing.",
    )
    group_show_add.add_argument(
        "--list",
        help="List the current subdomains (A records) for `domain`",
        action="store_true",
    )


def configure_show_info_subparser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser_show_info = subparsers.add_parser(
        name="show-info",
        help="Show information about do_ddns, including current configuration and version.",
    )

    parser_show_info.set_defaults(func=info.show_current_info)
    parser_show_info.add_argument(
        "--show-api-key",
        help="Display the unmasked API key in output.",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    sub_sub_parsers = parser_show_info.add_subparsers()
    parser_show_info_domains = sub_sub_parsers.add_parser(
        "domains",
        help="Show info for domains associated with this account.",
    )
    parser_show_info_domains.set_defaults(func=domains.show_all_domains)


def setup_argparse():
    parser = argparse.ArgumentParser(
        prog="do_ddns",
        description=textwrap.dedent(
            """
            Application to manage domains from DigitalOcean account as dynamic DNS domain(s).
            The app only supports IPv4. IPv6 may come in a future release.

            You'll always find the latest version on https://github.com/nivintw/ddns
            For bugs, suggestions, pull requests visit https://github.com/nivintw/ddns/issues
            """
        ).strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subparser_name")
    parser_update_ips = subparsers.add_parser(
        name="update-ips",
        help=("Update the IP addresses for the subdomains that are configured."),
    )
    parser_update_ips.set_defaults(func=subdomains.update_all_managed_subdomains)

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

    configure_ip_lookup_subparser(subparsers)
    configure_manage_subparser(subparsers)
    configure_un_manage_subparser(subparsers)
    configure_show_info_subparser(subparsers)

    return parser
