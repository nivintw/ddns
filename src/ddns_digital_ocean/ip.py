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

import json
import logging
import time
import urllib.request
from argparse import Namespace
from datetime import datetime

import requests
from rich import print

from . import constants
from .api_key_helpers import get_api
from .database import connect_database

conn = connect_database(constants.database_path)


class NoIPResolverServerError(Exception):
    """Raised when there are no IP Resolver servers configured."""


class IPv6NotSupportedError(Exception):
    """Raised when the user attempts to configure IPv6."""


def view_or_update_ip_server(args: Namespace):
    """UX function: View or update IP server settings.

    Note: Currently, we only support one ip server, and only IPv4.
    """
    ipserver = args.url
    ip_type = args.ip_mode
    if ipserver is not None:
        config_ip_server(ipserver, ip_type)

    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM ipservers").fetchone()
    ip4server = "[red]None Configured[/red]" if row is None else row["URL"]
    print("==== Upstream IP Address Resolver Servers ====")
    print(f"IP v4 resolver 	: [b]{ip4server}[/b]")


def config_ip_server(ipserver, ip_type):
    """Configure the server to use to retrieve our IP address.

    Right now, only one upstream IP resolver is supported.
    Current Limitations:
        1. Only IPv4 is supported.
        2. The code is written to support only one row/ip server configuration.
        3. The code can "store" an IPv6 server address,
            but the other code will not _use_ this server to perform a lookup.
    """
    cursor = conn.cursor()
    if ip_type == "4":
        cursor.execute(
            "INSERT INTO ipservers "
            "(id, URL, ip_version) "
            "values (1, :url, '4') "
            "ON CONFLICT(id) DO UPDATE SET URL=:url",
            {"url": ipserver},
        )
        conn.commit()
        print(f"IP resolver set to ({ipserver}) for ipv{ip_type}.")

    elif ip_type == "6":
        print("IPv6 is not currently supported.")
        raise IPv6NotSupportedError()


def get_ip():
    """Retrieve the hosts public IP address.

    Requires that an IP Resolver server has been configured.

    Raises:
        NoIPResolverServerError: No upstream IP Resolver server configured. Add one.
        Exception: Any exception raised while trying to resolve the public IP address of the host.
    """
    cursor = conn.cursor()
    # TODO: add support for multiple ip resolvers?
    row = cursor.execute("SELECT URL from ipservers where ip_version = '4'").fetchone()
    if row is None:
        raise NoIPResolverServerError("Please configure an IP resolver server.")

    server = row["URL"]
    try:
        response = requests.get(server, timeout=60)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(time.strftime("%Y-%m-%d %H:%M") + " - Error : " + str(e))
        raise


def updateip(args: Namespace):
    force: bool = args.force

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
        # Check if an update is required
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
