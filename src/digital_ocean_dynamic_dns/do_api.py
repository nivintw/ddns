# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Digital Ocean API helpers for managing DNS A records."""

import logging
import time
from collections.abc import Generator
from http import HTTPStatus
from string import ascii_letters, digits
from typing import Any

import requests
from more_itertools import countable
from rich import print as rprint

from .api_key_helpers import get_api
from .exceptions import NonSimpleDomainNameError

logger = logging.getLogger(__name__)


def get_a_records(domain: str) -> Generator[dict[str, Any]]:
    """Retrieve A records for `domain` from Digital Ocean."""
    apikey = get_api()
    page_results_limit = 20

    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"https://api.digitalocean.com/v2/domains/{domain}/records",
        headers=headers,
        timeout=45,
        params={"type": "A", "per_page": page_results_limit},
    )
    response.raise_for_status()
    response_data = response.json()
    domain_records = countable(response_data["domain_records"])

    yield from domain_records
    page = 1
    while domain_records.items_seen == page_results_limit:
        page += 1
        response = requests.get(
            f"https://api.digitalocean.com/v2/domains/{domain}/records",
            headers=headers,
            timeout=45,
            params={"type": "A", "per_page": page_results_limit, "page": page},
        )
        response.raise_for_status()
        response_data = response.json()
        domain_records = countable(response_data["domain_records"])
        yield from domain_records


def get_a_record_by_name(subdomain: str, domain: str) -> Generator[dict[str, Any], None, None]:
    """Retrieve a potentially existing A record by it's name."""
    apikey = get_api()
    page_results_limit = 20

    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"https://api.digitalocean.com/v2/domains/{domain}/records",
        headers=headers,
        timeout=45,
        params={"name": f"{subdomain}.{domain}", "type": "A", "per_page": page_results_limit},
    )
    response.raise_for_status()
    response_data = response.json()
    domain_records = countable(response_data["domain_records"])

    yield from domain_records
    page = 1
    while domain_records.items_seen == page_results_limit:
        page += 1
        response = requests.get(
            f"https://api.digitalocean.com/v2/domains/{domain}/records",
            headers=headers,
            timeout=45,
            params={
                "name": f"{subdomain}.{domain}",
                "type": "A",
                "per_page": page_results_limit,
                "page": page,
            },
        )
        response.raise_for_status()
        response_data = response.json()
        domain_records = countable(response_data["domain_records"])
        yield from domain_records


def get_a_record(domain_record_id: str, domain: str) -> dict[str, Any]:
    """Return the A record for `subdomain`."""
    apikey = get_api()
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"https://api.digitalocean.com/v2/domains/{domain}/records/{domain_record_id}",
        headers=headers,
        timeout=45,
    )
    response.raise_for_status()
    return response.json()["domain_record"]


def update_a_record(domain_record_id: str, domain: str, new_ip_address: str) -> dict[str, Any]:
    """Update an existing A record."""
    apikey = get_api()
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    data = {"type": "A", "data": new_ip_address}
    response = requests.patch(
        f"https://api.digitalocean.com/v2/domains/{domain}/records/{domain_record_id}",
        headers=headers,
        json=data,
        timeout=45,
    )
    response.raise_for_status()
    return response.json()["domain_record"]


def create_a_record(subdomain: str, domain: str, ip4_address: str) -> str:
    """Create an A record for subdomain.

    This function will _not_ manage the state of the local database.

    Returns:
        (str): The domain record id returned from the Digital Ocean API.
    """
    if set(domain).difference(ascii_letters + "." + digits + "-" + "@") or set(
        subdomain
    ).difference(ascii_letters + "." + digits + "-" + "@"):
        rprint("[red]Error:[/red] Give the domain name in simple form e.g. [b]test.domain.com[/b]")
        msg = "Error: Give the domain name in simple form e.g. test.domain.com"
        raise NonSimpleDomainNameError(msg)

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
        json=data,
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()

    rprint(f"An A record for {subdomain}.{domain} has been added.")
    logger.info(
        "%s - Info : subdomain %s.%s added", time.strftime("%Y-%m-%d %H:%M"), subdomain, domain
    )
    response_data = response.json()
    return response_data["domain_record"]["id"]


def verify_domain_is_registered(domain: str) -> None:
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
    if response.status_code == HTTPStatus.OK:
        return
    if response.status_code == HTTPStatus.NOT_FOUND:
        # Print an additional helpful message specifically for 404.
        rprint(f"Domain {domain} was not found associated with this digital ocean account.")

    response.raise_for_status()


def get_all_domains() -> Generator[dict[str, str], None, None]:
    """Return all domains associated with this account."""
    apikey = get_api()

    page_results_limit = 20

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
    domains = countable(response_data["domains"])
    yield from domains

    page = 1
    while domains.items_seen == page_results_limit:
        page += 1
        response = requests.get(
            "https://api.digitalocean.com/v2/domains/",
            headers=headers,
            timeout=45,
            params={"per_page": page_results_limit, "page": page},
        )
        response.raise_for_status()
        response_data = response.json()
        domains = countable(response_data["domains"])
        yield from domains
