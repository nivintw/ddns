# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

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
    cursor.execute("SELECT COUNT(*) FROM domains WHERE name = ? and managed = 1", (domain,))
    count = cursor.fetchone()[0]
    if count != 0:
        # domain is already being managed; nothing to do.
        return

    do_api.verify_domain_is_registered(domain)

    update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with conn:
        conn.execute(
            "INSERT INTO domains(name, cataloged, last_managed) "
            " values(:name, :cataloged, :last_managed) "
            "ON CONFLICT (name) DO UPDATE SET managed = 1, last_managed = :last_managed",
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
    cursor = conn.cursor()
    row = cursor.execute(
        "select id from domains where name = ? and managed = 1", (domain,)
    ).fetchone()
    if row is None:
        print(f"The domain [b]{domain}[/b] is not managed by digital-ocean-dynamic-dns.")
        return
    domain_id = row["id"]

    with conn:
        subs_res = conn.execute(
            "UPDATE subdomains SET managed = 0 WHERE main_id = :domain_id and managed = 1",
            {"domain_id": domain_id},
        )
        conn.execute(
            "UPDATE domains set managed = 0 where id = :domain_id", {"domain_id": domain_id}
        )
        print(
            f"Domain {domain} is no longer managed. "
            f"{subs_res.rowcount} related subdomains also no longer managed."
        )


def show_all_domains(_: Namespace):
    """Show information for domains associated with this Digital Ocean account.

    Args:
        _ (Namespace): Parsed CLI args. Not used here.
            Must be passed to this function because of how function martialing works.
    """
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
