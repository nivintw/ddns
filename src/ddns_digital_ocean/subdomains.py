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
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech>
# and the ddns-digital-ocean contributors

#
# list_sub_domains -> list_managed_sub_domains?
# list_do_sub_domains -> list_unmanaged_sub_domains?
# edit_subdomain -> toggle_subdomain_management
# add_subdomain -> register_and_manage_subdomain
# local_add_subdomain -> manage_existing_subdomain
# remove_subdomain -> unregister_subdomain

import json
import logging
import time
import urllib.request
from datetime import datetime
from string import ascii_letters, digits

import requests
from rich import print

from . import constants
from .api_key_helpers import get_api
from .database import connect_database
from .ip import get_ip

conn = connect_database(constants.database_path)


def list_sub_domains(domain):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM domains WHERE name LIKE ?", (domain,))
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            "[red]Error: [/red]No such domain. "
            "Check spelling or use ddns -d to show all top domains."
        )
        return
    print(f"\n\nCurrent sub domains for [b]{domain}[/b]\n\n")
    print("Domain\t\t\t\tCreated\t\t\tUpdated\t\t\tChecked\t\t\tActive")
    print("=" * 114)
    cursor.execute("SELECT id FROM domains WHERE name LIKE ?", (domain,))
    topdomain_id = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subdomains WHERE main_id LIKE ?", (topdomain_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        print(f"[red]Error:[/red] No sub domains for [b]{domain}[/b]")
    else:
        cursor.execute(
            "SELECT name,last_updated,last_checked,created,active "
            "FROM subdomains "
            "WHERE main_id LIKE ?",
            (topdomain_id,),
        )
        subdomains = cursor.fetchall()
        for i in subdomains:
            active = "True" if i[4] == 1 else "False"
            topdomain = i[0] + "." + domain
            topdomain = f"{topdomain:<25}"
            print(topdomain + "\t" + i[3] + "\t" + i[1] + "\t" + i[2] + "\t" + active)
    print("\n")


def list_do_sub_domains(domain):
    apikey = get_api()
    cursor = conn.cursor()

    req = urllib.request.Request(
        "https://api.digitalocean.com/v2/domains/" + domain + '/records?type="A"/?per_page=200'
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + apikey)
    current = urllib.request.urlopen(req)  # noqa: S310
    remote = current.read().decode("utf-8")
    remoteData = json.loads(remote)
    print(f"Domains in your DigitalOcean account not in ddns DB for [b]{domain}[/b]")
    print("===================================================================")
    for k in remoteData["domain_records"]:
        if k["type"] == "A":
            cursor.execute("SELECT COUNT(*) FROM subdomains WHERE id like ?", (str(k["id"]),))
            count = cursor.fetchone()[0]
            if count == 0:
                print(k["name"] + "." + domain + "\t\tID : " + str(k["id"]))


def toggle_subdomain_management(domain):
    """Toggle management state for a locally catalogued subdomain.

    I.e. managed -> unmanaged and unmanaged -> managed.

    Assumptions:
      - The relevant subdomain has previously been catalogued in the local database.
    """
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        return

    parts = domain.split(".")
    if len(parts) > 3:
        top = parts[1] + "." + parts[2] + "." + parts[3]
        sub = parts[0]
    else:
        sub = parts[0]
        top = parts[1] + "." + parts[2]
    longtop = sub + "." + top
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM domains WHERE name like ? or name like ?",
        (
            top,
            longtop,
        ),
    )
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            f"[red]Error:[/red] Top domain [bold]{top}[/bold] does not exist in the DB. "
            "So I'm giving up!"
        )
        return

    cursor.execute(
        "SELECT COUNT(*) "
        "FROM subdomains "
        "WHERE name like ? "
        "  and main_id=(SELECT id from domains WHERE name like ? or name like ?)",
        (sub, top, longtop),
    )
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            f"[red]Error:[/red] Domain [bold]{domain}[/bold] does not exist in the DB."
            " So I'm giving up!"
        )
        return

    cursor.execute(
        "SELECT id,active "
        "FROM subdomains "
        "WHERE name like ? "
        "  and main_id=(SELECT id from domains WHERE name like ? or name like ?)",
        (sub, top, longtop),
    )
    domain_info = cursor.fetchone()
    subdomain_id = str(domain_info[0])
    status = domain_info[1]
    status = 0 if status == 1 else 1

    cursor.execute(
        "UPDATE subdomains SET active = ? WHERE id = ?",
        (
            status,
            subdomain_id,
        ),
    )
    logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : Status for domain {domain} changed")
    print(f"Status for domain {domain} changed")
    conn.commit()


def add_subdomain(domain):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        return

    parts = domain.split(".")
    if len(parts) > 3:
        top = parts[1] + "." + parts[2] + "." + parts[3]
        sub = parts[0]
    else:
        sub = parts[0]
        top = parts[1] + "." + parts[2]
    apikey = get_api()

    ip = get_ip()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (top,))
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            f"[red]Error:[/red] Top domain [bold]{top}[/bold] does not exist in the DB."
            f" Please add it with [i]ddns -t {top}[/i]."
        )
        return

    cursor.execute("SELECT id,name FROM domains WHERE name LIKE ?", (top,))
    topdomain = cursor.fetchone()
    topdomain_id = topdomain[0]
    cursor.execute(
        "SELECT count(*) FROM subdomains WHERE main_id LIKE ? AND name like ?",
        (
            topdomain_id,
            sub,
        ),
    )
    count = cursor.fetchone()[0]
    if count != 0:
        print(f"[red]Error:[/red] [bold]{domain}[/bold] already exists.")
        return

    data = {"name": sub, "data": ip, "type": "A", "ttl": 3600}
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.digitalocean.com/v2/domains/" + top + "/records",
        data=json.dumps(data),
        headers=headers,
        timeout=60,
    )
    if str(response) == "<Response [201]>":
        if response != "Fail":
            response_data = response.json()
            domainid = str(response_data["domain_record"]["id"])
            cursor.execute(
                "INSERT INTO subdomains values(?,?,?,?,?,?,?,?,?)",
                (
                    domainid,
                    topdomain_id,
                    sub,
                    ip,
                    None,
                    now,
                    now,
                    now,
                    1,
                ),
            )
            conn.commit()
            print(f"The domain {domain} has been added.")
            logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : subdomain {domain} added")
    else:
        return f"[red]Error: {response!s} [/red]"


def remove_subdomain(domain):
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        return

    parts = domain.split(".")
    if len(parts) > 3:
        top = parts[1] + "." + parts[2] + "." + parts[3]
        sub = parts[0]
    else:
        sub = parts[0]
        top = parts[1] + "." + parts[2]
    longtop = sub + "." + top
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM domains WHERE name like ? or name like ?",
        (
            top,
            longtop,
        ),
    )
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            f"[red]Error:[/red] Top domain [bold]{top}[/bold] does not exist in the DB. "
            "So I'm giving up!"
        )
        return

    cursor.execute(
        "SELECT COUNT(*) "
        "FROM subdomains "
        "WHERE name like ? "
        "  and main_id=(SELECT id from domains WHERE name like ? or name like ?)",
        (
            sub,
            top,
            longtop,
        ),
    )
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            f"[red]Error:[/red] Domain [bold]{domain}[/bold] does not exist in the DB. "
            "So I'm giving up!"
        )
        return

    apikey = get_api()
    cursor.execute(
        "SELECT id "
        "FROM subdomains "
        "WHERE name like ? "
        "  and main_id=("
        "    SELECT id from domains WHERE name like ? or name like ?"
        "  )",
        (
            sub,
            top,
            longtop,
        ),
    )
    subdomain_id = str(cursor.fetchone()[0])
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.delete(
        "https://api.digitalocean.com/v2/domains/" + top + "/records/" + subdomain_id,
        headers=headers,
        timeout=60 * 2,
    )
    if str(response) == "<Response [204]>":
        cursor.execute("DELETE from subdomains where id=?", (subdomain_id,))
        logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : Subdomain {domain} removed")
        conn.commit()
    else:
        print("[red]Error: [/red]An error occurred! Please try again later!")


def local_add_subdomain(domain, domainid):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        return

    parts = domain.split(".")
    if len(parts) > 3:
        top = parts[1] + "." + parts[2] + "." + parts[3]
        sub = parts[0]
    else:
        sub = parts[0]
        top = parts[1] + "." + parts[2]
    longtop = sub + "." + top

    ip = get_ip()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM domains WHERE name like ? or name like ?",
        (
            top,
            longtop,
        ),
    )
    count = cursor.fetchone()[0]
    if count == 0:
        print(
            f"[red]Error:[/red] Top domain [bold]{top}[/bold] does not exist in the DB."
            f" Please add it with [i]ddns -t {top}[/i]."
        )
    else:
        cursor.execute(
            "SELECT id FROM domains WHERE name LIKE ? or name like ?",
            (
                top,
                longtop,
            ),
        )
        topdomain_id = cursor.fetchone()
        topdomain_id = topdomain_id[0]
        cursor.execute(
            "SELECT count(*) FROM subdomains WHERE main_id LIKE ? AND name like ?",
            (
                topdomain_id,
                sub,
            ),
        )
        count = cursor.fetchone()[0]
        if count != 0:
            print(f"[red]Error:[/red] [bold]{domain}[/bold] already exists.")
        else:
            cursor.execute(
                "INSERT INTO subdomains values(?,?,?,?,?,?,?,?,?)",
                (
                    domainid,
                    topdomain_id,
                    sub,
                    ip,
                    None,
                    now,
                    now,
                    now,
                    1,
                ),
            )
            conn.commit()
            print(f"The domain {domain} has been added.")
