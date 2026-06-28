# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Helpers for retrieving and validating the Digital Ocean API key."""

import os

from rich import print as rprint


class NoAPIKeyError(Exception):
    """Raised when the user tries to do anything without first configuring an API key."""


def get_api() -> str:
    """Retrieve the Digital Ocean API Token.

    There are currently two available sources for configuring the
      Digital Ocean API Token.

    The list below is ordered by precedence (i.e. the first value found is used):
        1. Environment variable DIGITALOCEAN_TOKEN
            - This is name that the official Digital Ocean Python
                library [pydo](https://pydo.readthedocs.io/en/latest/) uses.
        2. The value stored in the database.
    """
    api_token = os.environ.get("DIGITALOCEAN_TOKEN")
    if api_token is None:
        rprint(
            "[red]Error:[/red] Missing APIkey. "
            "Please set the DIGITALOCEAN_TOKEN environment variable!"
        )
        msg = "Missing API key. Please set the DIGITALOCEAN_TOKEN environment variable!"
        raise NoAPIKeyError(msg)

    return api_token
