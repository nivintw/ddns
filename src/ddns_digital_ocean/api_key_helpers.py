import logging
import time
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
    cursor = conn.cursor()

    cursor.execute("SELECT api FROM apikey")
    row = cursor.fetchone()

    if row is None:
        print("[red]Error:[/red] Missing APIkey. Please add one!")
        raise NoAPIKeyError("Missing API key. Please add one!")

    return row[0]


def set_api_key(api_value):
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM apikey")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("INSERT INTO apikey values(?,?)", (1, api_value))
            logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : API key added")
            print("Your API key has been added.")
        else:
            cursor.execute("UPDATE apikey SET api = ? WHERE id = 1", (api_value,))
            logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : API key updated")
            print("Your API key has been updated.")
