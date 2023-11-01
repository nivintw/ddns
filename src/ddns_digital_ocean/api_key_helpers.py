import logging
import time

from rich import print

from . import constants
from .database import connect_database

conn = connect_database(constants.database_path)


def get_api() -> str:
    cursor = conn.cursor()

    cursor.execute("SELECT api FROM apikey")
    try:
        row = cursor.fetchone()
    except Exception:
        print("[red]Error:[/red] Missing APIkey. Please add one!")
        raise
    else:
        return row[0]


def api(api_value):
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
    conn.commit()
