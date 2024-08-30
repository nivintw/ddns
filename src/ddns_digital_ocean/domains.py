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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech> and the ddns-digital-ocean contributors


import logging
import time
from argparse import Namespace

import requests
from rich import print

from . import constants
from .api_key_helpers import get_api
from .database import connect_database

conn = connect_database(constants.database_path)


def add_domain(domain):
    apikey = get_api()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (domain,))
    count = cursor.fetchone()[0]
    if count != 0:
        print(f"[red]Error:[/red] Domain name ({domain}) already in database!")
        return

    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        "https://api.digitalocean.com/v2/domains/" + domain,
        headers=headers,
        timeout=45,
    )
    response_data = response.json()

    if response.status_code == 401:
        print(
            "[red]Error: [/red]"
            "The api key that is configured resulted in an unauthorized response.\n"
            "Please configure a valid Digital Ocean API key to use."
            f"Response: {response_data}"
        )
        return
    elif response.status_code == 404:
        print(
            "[red]Error: [/red]The domain does not exist in your DigitalOcean account.\n"
            "Please add the domain from your control panel "
            "[b]https://cloud.digitalocean.com/networking/domains/[/b]"
        )
        return
    elif response.status_code == 429:
        print("[red]Error: [/red]API Rate limit exceeded. Please try again later.")
        return
    elif response.status_code == 500:
        print(
            "[red]Error: [/red]"
            "Unexpected Internal Server Error Response from DigitalOcean. "
            "Please try again later."
        )
        return
    elif response.status_code != requests.codes.ok:
        print(
            "[red]Error: [/red]"
            "Completely unexpected error response from Digital Ocean."
            "This is neat. If you see this more than once, open a ticket."
            f"Response: {response_data}"
        )
        return

    cursor.execute(
        "INSERT INTO domains values(?,?)",
        (
            None,
            domain,
        ),
    )
    print(f"The domain [b]{domain}[/b] has been added to the DB")
    logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : Domain {domain} added")
    conn.commit()


def show_all_domains():
    cursor = conn.cursor()
    apikey = get_api()

    page_results_limit = 200

    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        "https://api.digitalocean.com/v2/domains/",
        headers=headers,
        timeout=45,
        params={"per_page": page_results_limit},
    )
    response_data = response.json()
    if response_data["meta"]["total"] == 0:
        print("No domains associated with this Digital Ocean account!")

    print("Domains in database are marked with a [*]")
    print("================================================")
    for k in response_data["domains"]:
        cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (k["name"],))
        count = cursor.fetchone()[0]
        if count != 0:
            print("Name : [bold]" + k["name"] + " [*][/bold]")
        else:
            print("Name : " + k["name"])

    page = 1
    while response_data["meta"]["total"] == page_results_limit:
        page += 1
        response = requests.get(
            "https://api.digitalocean.com/v2/domains/",
            headers=headers,
            timeout=45,
            params={"per_page": page_results_limit, "page": page},
        )
        response_data = response.json()
        for k in response_data["domains"]:
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
        add_domain(args.add)
