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
    apikey = get_api()
    cursor = conn.cursor()
    if apikey is None:
        print("[red]Error:[/red] Missing APIkey. Please add one!")
    else:
        cursor.execute("SELECT COUNT(*) FROM domains WHERE name LIKE ?", (domain,))
        count = cursor.fetchone()[0]
        if count == 0:
            print(
                "[red]Error: [/red]No such domain. "
                "Check spelling or use ddns -d to show all top domains."
            )
        else:
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
    if apikey is None:
        print("[red]Error:[/red] Missing APIkey. Please add one!")
    else:
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


def edit_subdomain(domain):
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
    else:
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
        else:
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
            else:
                apikey = get_api()
                if apikey is None:
                    print("[red]Error:[/red] Missing APIkey. Please add one!")
                else:
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
                    logging.info(
                        time.strftime("%Y-%m-%d %H:%M")
                        + f" - Info : Status for domain {domain} changed"
                    )
                    print(f"Status for domain {domain} changed")
                    conn.commit()


def add_subdomain(domain):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
    else:
        parts = domain.split(".")
        if len(parts) > 3:
            top = parts[1] + "." + parts[2] + "." + parts[3]
            sub = parts[0]
        else:
            sub = parts[0]
            top = parts[1] + "." + parts[2]
        apikey = get_api()
        if apikey is None:
            print("[red]Error:[/red] Missing APIkey. Please add one!")
        else:
            ip = get_ip()
            if ip is None or "urlopen error" in ip:
                print(
                    "[red]Error:[/red] Failed to get public IP. "
                    f"Do you have a typo in your URI? [red]Error {ip}.[/red]"
                )
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (top,))
                count = cursor.fetchone()[0]
                if count == 0:
                    print(
                        f"[red]Error:[/red] Top domain [bold]{top}[/bold] does not exist in the DB."
                        f" Please add it with [i]ddns -t {top}[/i]."
                    )
                else:
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
                    else:
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
                                logging.info(
                                    time.strftime("%Y-%m-%d %H:%M")
                                    + f" - Info : subdomain {domain} added"
                                )
                        else:
                            return f"[red]Error: {str(response)} [/red]"


def remove_subdomain(domain):
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
    else:
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
        else:
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
            else:
                apikey = get_api()
                if apikey is None:
                    print("[red]Error:[/red] Missing APIkey. Please add one!")
                else:
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
                        "https://api.digitalocean.com/v2/domains/"
                        + top
                        + "/records/"
                        + subdomain_id,
                        headers=headers,
                        timeout=60 * 2,
                    )
                    if str(response) == "<Response [204]>":
                        cursor.execute("DELETE from subdomains where id=?", (subdomain_id,))
                        logging.info(
                            time.strftime("%Y-%m-%d %H:%M")
                            + f" - Info : Subdomain {domain} removed"
                        )
                        conn.commit()
                    else:
                        print("[red]Error: [/red]An error occurred! Please try again later!")


def local_add_subdomain(domain, domainid):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
    else:
        parts = domain.split(".")
        if len(parts) > 3:
            top = parts[1] + "." + parts[2] + "." + parts[3]
            sub = parts[0]

        else:
            sub = parts[0]
            top = parts[1] + "." + parts[2]
        apikey = get_api()
        longtop = sub + "." + top
        if apikey is None:
            print("[red]Error:[/red] Missing APIkey. Please add one!")
        else:
            ip = get_ip()
            if ip is None or "urlopen error" in ip:
                print(
                    "[red]Error:[/red] Failed to get public IP. "
                    f"Do you have a typo in your URI? [red]Error {ip}.[/red]"
                )
            else:
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
