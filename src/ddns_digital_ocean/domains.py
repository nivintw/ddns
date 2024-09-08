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


def manage_all_existing_A_records(domain: str, domain_id: str):
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
