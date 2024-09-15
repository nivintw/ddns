# digital-ocean-dynamic-dns
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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the digital-ocean-dynamic-dns contributors

import datetime as dt
import logging
import os
from argparse import Namespace

from rich import print

from . import constants
from .database import connect_database

conn = connect_database(constants.database_path)


class NoAPIKeyError(Exception):
    """Raised when the user tries to do anything without first configuring an API key."""


def view_or_update(args: Namespace):
    """UX function that will update or show the API key value."""

    api_key = args.api_key_value

    if api_key is None:
        curr_key = get_api()
        print(f"Current API key is: {curr_key}")
        return
    else:
        set_api_key(api_key)


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
    if api_token:
        return api_token

    cursor = conn.cursor()

    cursor.execute("SELECT key FROM apikey")
    row = cursor.fetchone()

    if row is None:
        print("[red]Error:[/red] Missing APIkey. Please add one!")
        raise NoAPIKeyError("Missing API key. Please add one!")

    return row["key"]


def set_api_key(api_value):
    with conn:
        now = dt.datetime.now()
        update_datetime = now.strftime("%Y-%m-%d %H:%M")

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM apikey")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute(
                "INSERT INTO apikey values(:id, :key, :last_updated)",
                {"id": 1, "key": api_value, "last_updated": update_datetime},
            )
            logging.info(update_datetime + " - Info : API key added")
            print("Your API key has been added.")
        else:
            cursor.execute(
                "UPDATE apikey SET key = :key, last_updated = :last_updated WHERE id = 1",
                {"key": api_value, "last_updated": update_datetime},
            )
            logging.info(update_datetime + " - Info : API key updated")
            print("Your API key has been updated.")
