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

#
# list_sub_domains -> list_managed_sub_domains?
# list_do_sub_domains -> list_unmanaged_sub_domains?
# add_subdomain -> register_and_manage_subdomain
# remove_subdomain -> unregister_subdomain

import logging
import time
from argparse import Namespace
from datetime import datetime
from string import ascii_letters, digits

from more_itertools import peekable
from rich.console import Console
from rich.table import Table

from . import constants, do_api
from .database import connect_database
from .exceptions import NonSimpleDomainNameError
from .ip import get_ip


class NoManagedSubdomainsError(Exception):
    """updated_all_managed_subdomains was called and there are no configured subdomains."""


class TopDomainNotManagedError(Exception):
    """Raised when the top domain specified is not managed.
    This error should never be raised by user-facing code paths.
    I.e. all user-facing code paths are required to manage the top domain
      before managing the sub-domains/A records.
    """


conn = connect_database(constants.database_path)


def list_sub_domains(domain):
    cursor = conn.cursor()
    console = Console()

    domain_A_records = {x["name"]: x for x in do_api.get_A_records(domain)}

    row = cursor.execute("SELECT id FROM domains WHERE name = ?", (domain,)).fetchone()
    if row is None:
        managed_subdomains = {}
    else:
        topdomain_id = row["id"]

        subdomains = cursor.execute(
            "SELECT "
            "  subdomains.name as name,"
            "  current_ip4,"
            "  last_updated,"
            "  last_checked,"
            "  subdomains.cataloged,"
            "  subdomains.managed "
            "FROM subdomains "
            "INNER JOIN domains on subdomains.main_id = domains.id "
            "WHERE main_id = ?",
            (topdomain_id,),
        ).fetchall()
        managed_subdomains = {x["name"]: x for x in subdomains}

    unmanaged_domain_records = domain_A_records.keys() - managed_subdomains.keys()
    managed_domain_records = domain_A_records.keys() & managed_subdomains.keys()

    if managed_domain_records:
        table = Table(title=f"Managed A records for [b]{domain}[/b]", highlight=True)
        table.add_column("Name/Subdomain")
        table.add_column("Current IPv4")
        table.add_column("First Managed")
        table.add_column("Last Checked")
        table.add_column("Last Updated")
        table.add_column("Currently Managed")

        for subdomain in managed_domain_records:
            row = managed_subdomains[subdomain]
            active = "True" if row["managed"] == 1 else "False"
            table.add_row(
                row["name"],
                row["current_ip4"],
                row["cataloged"],
                row["last_checked"],
                row["last_updated"],
                active,
            )

        console.print(table)
    else:
        console.print(f"No managed A records for [b]{domain}[/b]")

    if unmanaged_domain_records:
        table = Table(title=f"Unmanaged A records for [b]{domain}[/b]")
        table.add_column("Name/Subdomain")
        table.add_column("Domain Record Id")

        for domain_record_name in unmanaged_domain_records:
            table.add_row(domain_record_name, str(domain_A_records[domain_record_name]["id"]))

        console.print(table)
    else:
        console.print(f"No unmanaged A records for [b]{domain}[/b]")


def manage_subdomain(subdomain: str, domain: str):
    """Configure subdomain for management by digital-ocean-dynamic-dns.

    subdomain:
        The Hostname for the A record that will be created.
        Can be either "bare" (e.g. "@", "www")
            or a super-string of domain e.g. "@.example.com.", "blog.example.com".
    domain:
        The name of the Domain registered with Digital Ocean.

    """
    console = Console()
    if set(subdomain).difference(ascii_letters + "." + digits + "-" + "@"):
        console.print(
            "[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]"
        )
        raise NonSimpleDomainNameError()

    # Handle e.g. subdomain = "@.example.com", domain="example.com"
    subdomain = subdomain.removesuffix("." + domain)

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id FROM domains WHERE name = ? and managed = 1",
        (domain,),
    ).fetchone()

    if row is None:
        console.print(
            f"[red]Error:[/red] [bold]{domain}[/bold] is not a managed domain. "
            "We do [bold]not[/bold] expect users to ever be exposed to this error. "
            "If you see this in the console while using digital-ocean-dynamic-dns please"
            " open an issue on the repository."
        )
        raise TopDomainNotManagedError(f"domain {domain} not found in local database.")
    domain_id = row["id"]

    cursor.execute(
        "SELECT count(*) FROM subdomains WHERE main_id = ? AND name = ? and managed = 1",
        (
            domain_id,
            subdomain,
        ),
    )
    count = cursor.fetchone()[0]
    if count != 0:
        console.print(
            f"[yellow]Warning:[/yellow] [bold]{subdomain}[/bold]"
            " is already being managed by digital-ocean-dynamic-dns."
        )
        return

    ip = get_ip()
    # check to see if there's an existing A record.
    found_domain_records = peekable(do_api.get_A_record_by_name(subdomain, domain))
    if domain_record := found_domain_records.peek(None):
        # NOTE: strictly speaking, there could be multiple...
        # we only care if there's at least 1 already existing.
        # we will assume management of the first (unordered) A record we find that
        # has a matching name.
        domain_record_id = domain_record["id"]
        do_api.update_A_record(
            domain_record_id=domain_record_id,
            domain=domain,
            new_ip_address=ip,
        )
    else:
        domain_record_id = do_api.create_A_record(subdomain, domain, ip)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO subdomains("
        "   domain_record_id,"
        "   main_id,"
        "   name,"
        "   current_ip4,"
        "   cataloged,"
        "   last_checked,"
        "   last_updated"
        ") values("
        "   :domain_record_id,"
        "   :main_id,"
        "   :name,"
        "   :current_ip4,"
        "   :cataloged,"
        "   :last_checked,"
        "   :last_updated"
        ") ON CONFLICT(domain_record_id) DO UPDATE SET "
        "    managed = 1, "
        "    last_checked = :last_checked, "
        "    last_updated = :last_updated ",
        {
            "domain_record_id": domain_record_id,
            "main_id": domain_id,
            "name": subdomain,
            "current_ip4": ip,
            "cataloged": now,
            "last_checked": now,
            "last_updated": now,
        },
    )
    conn.commit()
    console.print(
        f"The A record for the subdomain {subdomain} for domain {domain} is now"
        " being managed by digital-ocean-dynamic-dns!"
    )


def un_manage_subdomain(subdomain: str, domain: str):
    """Stop managing `subdomain` via digital-ocean-dynamic-dns.

    subdomain:
        The Hostname for the A record that will be created.
        Can be either "bare" (e.g. "@", "www")
            or a super-string of domain e.g. "@.example.com.", "blog.example.com".
    domain:
        The name of the Domain registered with Digital Ocean.

    Will not delete `subdomain` from the database.
    Marks `subdomain` as un-managed in the database.
    """
    console = Console()
    if set(subdomain).difference(ascii_letters + "." + digits + "-" + "@"):
        console.print(
            "[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]"
        )
        raise NonSimpleDomainNameError()

    # Handle e.g. subdomain = "@.example.com", domain="example.com"
    subdomain = subdomain.removesuffix("." + domain)

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id FROM domains WHERE name = ?",
        (domain,),
    ).fetchone()

    if row is None:
        console.print(f"[red]Error:[/red] [bold]{domain}[/bold] is not a managed domain. ")
        raise TopDomainNotManagedError(f"domain {domain} not found in local database.")
    domain_id = row["id"]

    row = cursor.execute(
        "SELECT domain_record_id FROM subdomains WHERE main_id = ? AND name = ? AND managed = 1",
        (
            domain_id,
            subdomain,
        ),
    ).fetchone()
    if row is None:
        console.print(
            f"[yellow]Warning:[/yellow] [bold]{subdomain}[/bold]"
            " is not being managed by digital-ocean-dynamic-dns."
        )
        return
    domain_record_id = row["domain_record_id"]

    with conn:
        conn.execute(
            "UPDATE subdomains SET "
            "   managed = 0 "
            "WHERE "
            "   domain_record_id = :domain_record_id",
            {
                "domain_record_id": domain_record_id,
            },
        )
        console.print(
            f"The A record for the subdomain {subdomain} for domain {domain} is "
            " no longer being managed by digital-ocean-dynamic-dns!"
        )


def update_all_managed_subdomains(args: Namespace):
    force: bool = args.force

    cursor = conn.cursor()

    rows = cursor.execute("SELECT domain_record_id FROM subdomains where managed = 1").fetchall()
    if not rows:
        print(
            "[red]Error: [/red]There are no dynamic domains active."
            " Start by adding a new domain with [i]ddns -s test.example.com[/i]"
        )
        raise NoManagedSubdomainsError()

    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    current_ip = get_ip()
    updated = None

    for subdomain_row in rows:
        domain_record_id = subdomain_row["domain_record_id"]
        domain_info = cursor.execute(
            "SELECT name "
            "FROM domains "
            "WHERE id = (SELECT main_id from subdomains WHERE domain_record_id = ?)",
            (domain_record_id,),
        ).fetchone()
        domain_name = str(domain_info["name"])

        # Check DO API to see if an update is required
        domain_record = do_api.get_A_record(
            domain_record_id=domain_record_id,
            domain=domain_name,
        )
        remoteIP4 = domain_record["data"]

        if remoteIP4 != current_ip or force is True:
            updated = True
            domain_record = do_api.update_A_record(
                domain_record_id=domain_record_id,
                domain=domain_name,
                new_ip_address=current_ip,
            )

            cursor.execute(
                "UPDATE subdomains "
                "SET "
                "  current_ip4 = :current_ip, "
                "  last_updated = :now, "
                "  last_checked = :now "
                "WHERE domain_record_id = :domain_record_id",
                {
                    "current_ip": current_ip,
                    "now": now,
                    "domain_record_id": domain_record_id,
                },
            )

            conn.commit()
        else:
            cursor.execute(
                "UPDATE subdomains "
                "SET last_checked=:now "
                "WHERE domain_record_id = :domain_record_id",
                {
                    "now": now,
                    "domain_record_id": domain_record_id,
                },
            )
            conn.commit()

    if updated is None:
        msg = time.strftime("%Y-%m-%d %H:%M") + " - Info : No updates necessary"
        print(msg)
        logging.info(msg)
    else:
        msg = (
            time.strftime("%Y-%m-%d %H:%M")
            + " - Info : Updates done. Use ddns -l domain.com to check domain"
        )
        print(msg)
        logging.info(msg)


# def records_delete(subdomain: str, domain: str):
#     if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
#         print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
#         return
#     cursor = conn.cursor()

#     cursor.execute(
#         "SELECT id FROM domains WHERE name like ?",
#         (domain,),
#     )
#     cursor.execute(
#         "SELECT COUNT(*) FROM domains WHERE name like ? or name like ?",
#         (
#             top,
#             longtop,
#         ),
#     )
#     count = cursor.fetchone()[0]
#     if count == 0:
#         print(
#             f"[red]Error:[/red] Top domain [bold]{top}[/bold] does not exist in the DB. "
#             "So I'm giving up!"
#         )
#         return

#     cursor.execute(
#         "SELECT COUNT(*) "
#         "FROM subdomains "
#         "WHERE name like ? "
#         "  and main_id=(SELECT id from domains WHERE name like ? or name like ?)",
#         (
#             sub,
#             top,
#             longtop,
#         ),
#     )
#     count = cursor.fetchone()[0]
#     if count == 0:
#         print(
#             f"[red]Error:[/red] Domain [bold]{domain}[/bold] does not exist in the DB. "
#             "So I'm giving up!"
#         )
#         return

#     apikey = get_api()
#     cursor.execute(
#         "SELECT id "
#         "FROM subdomains "
#         "WHERE name like ? "
#         "  and main_id=("
#         "    SELECT id from domains WHERE name like ? or name like ?"
#         "  )",
#         (
#             sub,
#             top,
#             longtop,
#         ),
#     )
#     subdomain_id = str(cursor.fetchone()[0])
#     headers = {
#         "Authorization": "Bearer " + apikey,
#         "Content-Type": "application/json",
#     }
#     response = requests.delete(
#         "https://api.digitalocean.com/v2/domains/" + top + "/records/" + subdomain_id,
#         headers=headers,
#         timeout=60 * 2,
#     )
#     if str(response) == "<Response [204]>":
#         cursor.execute("DELETE from subdomains where id=?", (subdomain_id,))
#         logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : Subdomain {domain} removed")
#         conn.commit()
#     else:
#         print("[red]Error: [/red]An error occurred! Please try again later!")
