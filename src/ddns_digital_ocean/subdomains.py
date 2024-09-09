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

from rich import print

from . import constants, do_api
from .database import connect_database
from .ip import get_ip


class NoConfiguredSubdomainsError(Exception):
    """updated_all_managed_subdomains was called and there are no configured subdomains."""


class TopDomainNotManagedError(Exception):
    """Raised when the top domain specified is not managed.
    This error should never be raised by user-facing code paths.
    I.e. all user-facing code paths are required to manage the top domain
      before managing the sub-domains/A records.
    """


class NonSimpleDomainNameError(Exception):
    """Supported domain names must be in a simple format.
    i.e. ascii_letters + "." + digits + "-" + "@"
    """

    # TODO: move this to top-level exceptions.py and
    #   use this same exception class in do_api.py.


conn = connect_database(constants.database_path)


def list_sub_domains(domain):
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM domains WHERE name LIKE ?", (domain,))
    row = cursor.fetchone()
    if row is None:
        print(
            "[red]Error: [/red]No such domain. "
            "Check spelling or use ddns -d to show all top domains."
        )
        return
    topdomain_id = row["id"]

    subdomains = cursor.execute(
        "SELECT name,last_updated,last_checked,created,active "
        "FROM subdomains "
        "WHERE main_id LIKE ?",
        (topdomain_id,),
    ).fetchall()

    if not subdomains:
        print(f"[red]Error:[/red] No sub domains for [b]{domain}[/b]")
        return

    print(f"\n\nCurrent sub domains for [b]{domain}[/b]\n\n")
    print("Domain\t\t\t\tCreated\t\t\tUpdated\t\t\tChecked\t\t\tActive")
    print("=" * 114)
    for i in subdomains:
        active = "True" if i["active"] == 1 else "False"
        topdomain = i["name"] + "." + domain
        topdomain = f"{topdomain:<25}"
        print(
            topdomain
            + "\t"
            + i["created"]
            + "\t"
            + i["last_updated"]
            + "\t"
            + i["last_checked"]
            + "\t"
            + active
        )
    print("\n")


def list_do_unmanaged_sub_domains(domain):
    cursor = conn.cursor()
    domain_A_records = do_api.get_A_records(domain)

    print(f"Domains in your DigitalOcean account not in ddns DB for [b]{domain}[/b]")
    print("===================================================================")
    for k in domain_A_records:
        cursor.execute("SELECT COUNT(*) FROM subdomains WHERE id like ?", (str(k["id"]),))
        count = cursor.fetchone()[0]
        if count == 0:
            print(k["name"] + "." + domain + "\t\tID : " + str(k["id"]))


def manage_subdomain(subdomain: str, domain: str):
    """Configure subdomain for management by digital-ocean-dynamic-dns.

    subdomain:
        The Hostname for the A record that will be created.
        Can be either "bare" (e.g. "@", "www")
            or a super-string of domain e.g. "@.example.com.", "blog.example.com".
    domain:
        The name of the Domain registered with Digital Ocean.

    """
    if set(subdomain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        raise NonSimpleDomainNameError()

    # Handle e.g. subdomain = "@.example.com", domain="example.com"
    subdomain = subdomain.removesuffix("." + domain)

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id FROM domains WHERE name like ?",
        (domain,),
    ).fetchone()

    if row is None:
        print(
            f"[red]Error:[/red] [bold]{domain}[/bold] is not a managed domain. "
            "We do [bold]not[/bold] expect users to ever be exposed to this error. "
            "If you see this in the console while using digital-ocean-dynamic-dns please"
            " open an issue on the repository."
        )
        raise TopDomainNotManagedError(f"domain {domain} not found in local database.")
    domain_id = row["id"]

    cursor.execute(
        "SELECT count(*) FROM subdomains WHERE main_id LIKE ? AND name like ?",
        (
            domain_id,
            subdomain,
        ),
    )
    count = cursor.fetchone()[0]
    if count != 0:
        print(
            f"[yellow]Warning:[/yellow] [bold]{subdomain}[/bold]"
            " is already being managed by digital-ocean-dynamic-dns."
        )
        return

    ip = get_ip()
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
        ")",
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
    print(
        f"The A record for the subdomain {subdomain} for domain {domain} is now"
        " being managed by digital-ocean-dynamic-dns!"
    )


def update_all_managed_subdomains(args: Namespace):
    force: bool = args.force

    cursor = conn.cursor()

    rows = cursor.execute("SELECT domain_record_id,managed FROM subdomains").fetchall()
    if not rows:
        print(
            "[red]Error: [/red]There are no dynamic domains active."
            " Start by adding a new domain with [i]ddns -s test.example.com[/i]"
        )
        raise NoConfiguredSubdomainsError()

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
        subdomain_managed = subdomain_row["managed"]

        if not subdomain_managed:
            # Skip over subdomains that we used to manage but aren't currently.
            continue

        # Check DO API to see if an update is required
        # TODO: Use the current_ip4 value instead of calling to
        # DO-API unless force is specified...

        # so we don't have to query DO just to check.
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
