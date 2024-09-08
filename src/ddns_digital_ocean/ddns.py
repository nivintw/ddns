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
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

import logging
from string import ascii_letters, digits

from rich import print

from . import constants
from .args import setup_argparse
from .database import connect_database
from .ip import get_ip

logging.basicConfig(filename=constants.logfile, level=logging.INFO, format="%(message)s")


conn = connect_database(constants.database_path)


def domaininfo(domain):
    local_ip = get_ip()
    cursor = conn.cursor()
    if set(domain).difference(ascii_letters + "." + digits + "@" + "-"):
        print(
            "[red]Error:[/red]. Give the domain name in simple form "
            "e.g. [bold]test.domain.com[/bold]"
        )
        return

    parts = domain.split(".")
    if len(parts) > 3:
        top = parts[1] + "." + parts[2] + "." + parts[3]
    else:
        top = parts[1] + "." + parts[2]
    cursor.execute("SELECT id FROM domains WHERE name like ?", (top,))
    domain_id = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM subdomains WHERE main_id like ?", (domain_id,))
    domains = cursor.fetchall()
    local_ip = f"[red]{local_ip}[/red]" if local_ip != domains[0][3] else local_ip

    print(
        f"The domain [bold]{domain}[/bold] has the IP [bold]{domains[0][3]}[/bold]. "
        f"Your public IP is [bold]{local_ip}[/bold]."
    )


def run():
    # Commandline arguments
    parser = setup_argparse()

    args_raw = parser.parse_args()
    args = vars(args_raw)

    # TODO: update args to support multiple domains at the same time.
    # Right now, argparse has been updated to support multiple values but we haven't updated
    # this section to make multiple args actually work.

    if args["current"]:
        domaininfo(args["current"][0][0])

    elif args_raw.subparser_name in [
        "ip_lookup_config",
        "api_key",
        "update_ips",
        "logs",
        "show_info",
        "domains",
    ]:
        # NOTE: these subparsers have been configured.
        # eventually, all options will be handled similarly.
        args_raw.func(args_raw)


if __name__ == "__main__":
    run()
