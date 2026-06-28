# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Subdomain management for digital-ocean-dynamic-dns."""

import logging
import time
from argparse import Namespace
from datetime import UTC, datetime
from string import ascii_letters, digits

from more_itertools import peekable
from rich.console import Console
from rich.table import Table

from . import constants, do_api
from .database import connect_database
from .exceptions import NonSimpleDomainNameError
from .ip import get_ip

logger = logging.getLogger(__name__)


class NoManagedSubdomainsError(Exception):
    """updated_all_managed_subdomains was called and there are no configured subdomains."""


class TopDomainNotManagedError(Exception):
    """Raised when the top domain specified is not managed.

    This error should never be raised by user-facing code paths.
    I.e. all user-facing code paths are required to manage the top domain
      before managing the sub-domains/A records.
    """


conn = connect_database(constants.database_path)


def list_sub_domains(domain: str) -> None:
    """List managed and unmanaged A records for a domain.

    Args:
        domain: The top-level domain name registered with Digital Ocean.
    """
    cursor = conn.cursor()
    console = Console()

    domain_a_records = {x["name"]: x for x in do_api.get_a_records(domain)}

    row = cursor.execute("SELECT id FROM domains WHERE name = ?", (domain,)).fetchone()
    if row is None:
        managed_subdomains = {}
    else:
        topdomain_id = row["id"]

        subdomains = cursor.execute(
            "SELECT "
            "  subdomains.name as name,"
            "  domain_record_id,"
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
        managed_subdomains = {x["name"]: x for x in subdomains if x["managed"] == 1}

    unmanaged_domain_records = domain_a_records.keys() - managed_subdomains.keys()
    managed_domain_records = domain_a_records.keys() & managed_subdomains.keys()

    if managed_domain_records:
        table = Table(title=f"Managed A records for [b]{domain}[/b]", highlight=True)
        table.add_column("Name/Subdomain")
        table.add_column("Domain Record Id")
        table.add_column("IPv4 Address")
        table.add_column("First Managed")
        table.add_column("Last Checked")
        table.add_column("Last Updated")

        for subdomain in managed_domain_records:
            row = managed_subdomains[subdomain]
            table.add_row(
                row["name"],
                str(row["domain_record_id"]),
                row["current_ip4"],
                row["cataloged"],
                row["last_checked"],
                row["last_updated"],
            )

        console.print(table)
    else:
        console.print(f"No managed A records for [b]{domain}[/b]")

    if unmanaged_domain_records:
        table = Table(title=f"Unmanaged A records for [b]{domain}[/b]", highlight=True)
        table.add_column("Name/Subdomain")
        table.add_column("Domain Record Id")
        table.add_column("IPv4 Address")

        for domain_record_name in unmanaged_domain_records:
            table.add_row(
                domain_record_name,
                str(domain_a_records[domain_record_name]["id"]),
                str(domain_a_records[domain_record_name]["data"]),
            )

        console.print(table)
    else:
        console.print(f"No unmanaged A records for [b]{domain}[/b]")


def manage_subdomain(subdomain: str, domain: str) -> None:
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
        raise NonSimpleDomainNameError

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
        msg = f"domain {domain} not found in local database."
        raise TopDomainNotManagedError(msg)
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
    found_domain_records = peekable(do_api.get_a_record_by_name(subdomain, domain))
    if domain_record := found_domain_records.peek(None):
        # NOTE: strictly speaking, there could be multiple...
        # we only care if there's at least 1 already existing.
        # we will assume management of the first (unordered) A record we find that
        # has a matching name.
        domain_record_id = domain_record["id"]
        do_api.update_a_record(
            domain_record_id=domain_record_id,
            domain=domain,
            new_ip_address=ip,
        )
    else:
        domain_record_id = do_api.create_a_record(subdomain, domain, ip)

    now = datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M")
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


def un_manage_subdomain(subdomain: str, domain: str) -> None:
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
        raise NonSimpleDomainNameError

    # Handle e.g. subdomain = "@.example.com", domain="example.com"
    subdomain = subdomain.removesuffix("." + domain)

    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id FROM domains WHERE name = ?",
        (domain,),
    ).fetchone()

    if row is None:
        console.print(f"[red]Error:[/red] [bold]{domain}[/bold] is not a managed domain. ")
        msg = f"domain {domain} not found in local database."
        raise TopDomainNotManagedError(msg)
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
            "UPDATE subdomains SET managed = 0 WHERE domain_record_id = :domain_record_id",
            {
                "domain_record_id": domain_record_id,
            },
        )
        console.print(
            f"The A record for the subdomain {subdomain} for domain {domain} is "
            " no longer being managed by digital-ocean-dynamic-dns!"
        )


def update_all_managed_subdomains(args: Namespace) -> None:
    """Update all managed subdomains to the current public IP address.

    Args:
        args: Parsed CLI arguments; expects a ``force`` boolean attribute.
    """
    force: bool = args.force
    console = Console()

    cursor = conn.cursor()

    rows = cursor.execute("SELECT domain_record_id FROM subdomains where managed = 1").fetchall()
    if not rows:
        console.print(
            "[red]Error: [/red]There are no dynamic domains active."
            " Start by adding a new domain with [i]do_ddns manage[/i]."
            " E.g. [i]do_ddns manage example.com --sub-domain test[/i]."
        )
        raise NoManagedSubdomainsError

    now = datetime.now(tz=UTC).astimezone().strftime("%d-%m-%Y %H:%M")
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
        domain_record = do_api.get_a_record(
            domain_record_id=domain_record_id,
            domain=domain_name,
        )
        remote_ip4 = domain_record["data"]

        if remote_ip4 != current_ip or force is True:
            updated = True
            domain_record = do_api.update_a_record(
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
        console.print(msg)
        logger.info(msg)
    else:
        msg = (
            time.strftime("%Y-%m-%d %H:%M")
            + " - Info : Updates done. Use do_ddns manage <domain> --list to check <domain>"
        )
        console.print(msg)
        logger.info(msg)
