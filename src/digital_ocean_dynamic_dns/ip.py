# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

import logging
import time
from argparse import Namespace

import requests
from rich import print

from . import constants
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

    else:
        print("IPv6 is not currently supported.")
        raise IPv6NotSupportedError


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
        logging.exception(time.strftime("%Y-%m-%d %H:%M") + " - Error : " + str(e))
        raise
