import json
import logging
import time
import urllib.request
from datetime import datetime

import requests
from rich import print

from . import constants
from .api_key_helpers import get_api
from .database import connect_database

conn = connect_database(constants.database_path)


class NoIPResolverServerError(Exception):
    """Raised when there are no IP Resolver servers configured."""


def ip_server(ipserver, ip_type):
    """Configure the server to use to retrieve our IP address.

    Current Limitations:
        1. Only IPv4 is supported.
        2. The code is written to support only one row/ip server configuration.
        3. The code can "store" an IPv6 server address,
            but the other code will not _use_ this server to perform a lookup.
    """
    cursor = conn.cursor()
    if ip_type == "4":
        cursor.execute("SELECT COUNT(ip4_server) FROM ipservers")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("INSERT INTO ipservers values(?,?,?)", (None, ipserver, None))
            conn.commit()
            print(f"New IP resolver ({ipserver}) for ipv{ip_type} added.")
        else:
            cursor.execute("UPDATE ipservers SET ip4_server = ? WHERE id = 1", (ipserver,))
            print(f"IP resolver ({ipserver}) for ipv{ip_type} updated.")
            logging.info(
                time.strftime("%Y-%m-%d %H:%M")
                + f" - Info : IP resolver ({ipserver}) for ipv{ip_type} updated."
            )
            conn.commit()
    elif ip_type == "6":
        cursor.execute("SELECT COUNT(ip6_server) FROM ipservers")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("INSERT INTO ipservers values(?,?,?)", (None, None, ipserver))
            conn.commit()
            print(
                f"New IP resolver ({ipserver}) for ipv{ip_type} added. \n\r"
                " This IP version is not supported."
            )
        else:
            cursor.execute("UPDATE ipservers SET ip6_server = ? WHERE id = 1", (ipserver,))
            print(
                f"IP resolver ({ipserver}) for ipv{ip_type} updated. \n\r"
                " This IP version is not supported."
            )
            logging.info(
                time.strftime("%Y-%m-%d %H:%M")
                + f" - Info : IP resolver ({ipserver}) for ipv{ip_type} updated."
            )
            conn.commit()


def get_ip():
    """Retrieve the hosts public IP address.

    Requires that an IP Resolver server has been configured.

    Raises:
        NoIPResolverServerError: No upstream IP Resolver server configured. Add one.
        Exception: Any exception raised while trying to resolve the public IP address of the host.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(ip4_server) FROM ipservers")
    count = cursor.fetchone()[0]
    if count == 0:
        raise NoIPResolverServerError("Please configure an IP resolver server.")
    cursor.execute("SELECT ip4_server from ipservers")
    server = cursor.fetchone()[0]
    try:
        response = requests.get(server, timeout=60)
        return response.text
    except Exception as e:
        logging.error(time.strftime("%Y-%m-%d %H:%M") + " - Error : " + str(e))
        raise


def updateip(force):
    apikey = get_api()
    current_ip = get_ip()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM subdomains")
    count = cursor.fetchone()[0]
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    updated = None
    if count == 0:
        print(
            "[red]Error: [/red]There are no dynamic domains active."
            " Start by adding a new domain with [i]ddns -s test.example.com[/i]"
        )
        return

    cursor.execute("SELECT id,active FROM subdomains")
    rows = cursor.fetchall()
    for i in rows:
        cursor.execute(
            "SELECT name "
            "FROM domains "
            "WHERE id like (SELECT main_id from subdomains WHERE id = ?)",
            (i[0],),
        )
        domain_info = cursor.fetchone()
        domain_name = str(domain_info[0])
        domain_status = i[1]
        subdomain_id = str(i[0])
        # Chek if an update is required
        if domain_status == 1:
            req = urllib.request.Request(
                "https://api.digitalocean.com/v2/domains/"
                + domain_name
                + "/records/"
                + subdomain_id
            )
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", "Bearer " + apikey)
            current = urllib.request.urlopen(req)  # noqa: S310
            remote = current.read().decode("utf-8")
            remoteData = json.loads(remote)
            remoteIP4 = remoteData["domain_record"]["data"]
            if remoteIP4 != current_ip or force is True and domain_status == 1:
                updated = True
                data = {"type": "A", "data": current_ip}
                headers = {
                    "Authorization": "Bearer " + apikey,
                    "Content-Type": "application/json",
                }
                response = requests.patch(
                    "https://api.digitalocean.com/v2/domains/"
                    + domain_name
                    + "/records/"
                    + subdomain_id,
                    data=json.dumps(data),
                    headers=headers,
                    timeout=60,
                )
                if str(response) != "<Response [200]>":
                    logging.error(
                        time.strftime("%Y-%m-%d %H:%M")
                        + " - Error updating ("
                        + str(domain_name)
                        + ") : "
                        + str(response.content)
                    )
                else:
                    cursor.execute(
                        "UPDATE subdomains SET current_ip4=? WHERE id = ?",
                        (
                            current_ip,
                            subdomain_id,
                        ),
                    )
                    cursor.execute(
                        "UPDATE subdomains SET last_updated=? WHERE id = ?",
                        (
                            now,
                            subdomain_id,
                        ),
                    )
                    cursor.execute(
                        "UPDATE subdomains SET last_checked=? WHERE id = ?",
                        (
                            now,
                            subdomain_id,
                        ),
                    )
                    conn.commit()
            else:
                cursor.execute(
                    "UPDATE subdomains SET last_checked=? WHERE id = ?",
                    (
                        now,
                        subdomain_id,
                    ),
                )
                conn.commit()

    if updated is None:
        logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : No updated necessary")
    else:
        logging.info(
            time.strftime("%Y-%m-%d %H:%M")
            + " - Info : Updates done. Use ddns -l domain.com to check domain"
        )
