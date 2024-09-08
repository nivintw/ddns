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

import datetime as dt
import logging
from argparse import Namespace

from more_itertools import peekable
from rich import print

from . import constants, do_api
from .database import connect_database
from .subdomains import manage_subdomain

conn = connect_database(constants.database_path)


def manage_domain(domain):
    """Ensure <domain> is a registered domain for this account and mark as managed."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (domain,))
    count = cursor.fetchone()[0]
    if count != 0:
        # domain is already being managed; nothing to do.
        return

    do_api.verify_domain_is_registered(domain)

    update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with conn:
        conn.execute(
            "INSERT INTO domains(name, cataloged, last_managed) "
            " values(:name, :cataloged, :last_managed)",
            {
                "name": domain,
                "cataloged": update_datetime,
                "last_managed": update_datetime,
            },
        )
        print(f"The domain [b]{domain}[/b] has been added to the DB")
        logging.info(update_datetime + f" - Info : Domain {domain} added")


def manage_all_existing_A_records(domain: str):
    """Begin managing all existing A records for `domain`.

    Used to import existing externally created A records into digital-ocean-dynamic-dns.
    Upon subsequent runs of `do_ddns update` these A records will be automatically handled.
    """
    existing_A_records = do_api.get_A_records(domain)

    for record in existing_A_records:
        manage_subdomain(subdomain=record["name"], domain=domain)


def un_manage_domain(domain):
    """Mark the domain as unmanaged.

    Will not remove or deregister the associated domain.
    """
    # TODO: Implement.
    ...


def show_all_domains():
    cursor = conn.cursor()
    domains = peekable(do_api.get_all_domains())

    if domains.peek(None) is None:
        print("No domains associated with this Digital Ocean account!")
        return

    print("Domains in database are marked with a [*]")
    print("================================================")
    for k in domains:
        cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (k["name"],))
        count = cursor.fetchone()[0]
        if count != 0:
            print("Name : [bold]" + k["name"] + " [*][/bold]")
        else:
            print("Name : " + k["name"])


def main(args: Namespace):
    """Handle tlds subparser."""
    if args.list:
        show_all_domains()
    else:
        manage_domain(args.add)
