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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

import json
import logging
import time
from collections.abc import Generator
from string import ascii_letters, digits

import requests
from rich import print

from .api_key_helpers import get_api


def get_A_records(domain) -> dict:
    """Retrieve A records for `domain` from Digital Ocean."""
    apikey = get_api()
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"https://api.digitalocean.com/v2/domains/{domain}/records",
        headers=headers,
        timeout=45,
        params={"type": "A", "per_page": 200},
    )
    response.raise_for_status()

    return response.json()


def create_A_record(subdomain: str, domain: str, ip4_address: str) -> str:
    """Create an A record for subdomain.

    This function will _not_ manage the state of the local database.

    returns:
        (str): The domain record id returned from the Digital Ocean API.
    """
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@"):
        print("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        raise ValueError("Error: Give the domain name in simple form e.g. test.domain.com")

    apikey = get_api()

    # Handle e.g. subdomain = "@.example.com", domain="example.com"
    subdomain = subdomain.removesuffix("." + domain)

    data = {"name": subdomain, "data": ip4_address, "type": "A", "ttl": 3600}
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.digitalocean.com/v2/domains/" + domain + "/records",
        data=json.dumps(data),
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()

    print(f"An A record for {subdomain}.{domain} has been added.")
    logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : subdomain {domain} added")
    response_data = response.json()
    domain_record_id = str(response_data["domain_record"]["id"])
    return domain_record_id


def verify_domain_is_registered(domain: str):
    """Verify that the user-supplied `domain` is registered for the authenticated account."""
    apikey = get_api()
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        "https://api.digitalocean.com/v2/domains/" + domain,
        headers=headers,
        timeout=45,
    )
    if response.status_code == requests.codes.ok:
        return
    elif response.status_code == 404:
        # Print an additional helpful message specifically for 404.
        print(f"Domain {domain} was not found associated with this digital ocean account.")

    response.raise_for_status()


def get_all_domains() -> Generator[dict[str, str], None, None]:
    """Return all domains associated with this account."""
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
    response.raise_for_status()

    response_data = response.json()

    yield from response_data["domains"]
    page = 1
    while response_data["meta"]["total"] == page_results_limit:
        page += 1
        response = requests.get(
            "https://api.digitalocean.com/v2/domains/",
            headers=headers,
            timeout=45,
            params={"per_page": page_results_limit, "page": page},
        )
        response.raise_for_status()
        response_data = response.json()
        yield from response_data["domains"]
