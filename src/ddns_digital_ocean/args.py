# ddns-digital-ocean
# Copyright (C) 2023  Tyler Nivin <tyler@nivin.tech>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech> and the ddns-digital-ocean contributors

import argparse
import textwrap

from ddns_digital_ocean import api_key_helpers, info, ip, logs

from . import domains


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

    parser_tld = subparsers.add_parser(name="domains", help="View and configure domains.")
    parser_tld.set_defaults(func=domains.main)

    group_tld = parser_tld.add_mutually_exclusive_group(required=True)
    group_tld.add_argument(
        "-l",
        "--list",
        help="List domains registered in your DigitalOcean account, indicating which are managed.",
        action="store_true",
    )

    group_tld.add_argument(
        "-a",
        "--add",
        help="Add <domain> to domains managed by ddns-digital-ocean.",
        metavar=("<domain>"),
    )

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
        "-t",
        "--top",
        help=("Add new domain(s) from your DigitalOcean account to use as a dynamic DNS domain."),
        required=False,
        metavar=("domain"),
        nargs="+",
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
