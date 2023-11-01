import logging
import sqlite3
import time
from pathlib import Path
from sqlite3 import Error

from rich import print

from . import constants


def connect_database(database_path: Path):
    conn = None

    try:
        conn = sqlite3.connect(database_path)
    except Error as e:
        logging.error(time.strftime("%Y-%m-%d %H:%M") + " - Error : " + str(e))
        print(e)
        raise
    else:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS apikey
            (id integer NOT NULL PRIMARY KEY,
                api text NOT NULL)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS ipservers
        (id integer NOT NULL PRIMARY KEY,
            ip4_server text NOT NULL,
            ip6_server text)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS domains
        (id integer PRIMARY KEY,
            name text NOT NULL)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS subdomains
        (id integer PRIMARY KEY,
            main_id integer NOT NULL,
            name text NOT NULL,
            current_ip4 text NOT NULL,
            current_ip6 text NULL)"""
        )

        return conn


def updatedb():
    # Update DB with new column 20.03.23
    # Add last updated field for subdomains
    conn = connect_database(constants.database_path)
    new_column = "last_updated"
    info = conn.execute("PRAGMA table_info('subdomains')").fetchall()
    if not any(new_column in word for word in info):
        add_column = "ALTER TABLE subdomains ADD COLUMN last_updated text default 'N/A'"
        conn.execute(add_column)
        conn.commit()
        logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : Database updated")

    new_column = "last_checked"
    info = conn.execute("PRAGMA table_info('subdomains')").fetchall()
    if not any(new_column in word for word in info):
        add_column = "ALTER TABLE subdomains ADD COLUMN last_checked text default 'N/A'"
        conn.execute(add_column)
        conn.commit()
        logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : Database updated")

    new_column = "created"
    info = conn.execute("PRAGMA table_info('subdomains')").fetchall()
    if not any(new_column in word for word in info):
        add_column = "ALTER TABLE subdomains ADD COLUMN created text default '[b]Unknown     Info[/b]'"
        conn.execute(add_column)
        conn.commit()
        logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : Database updated")

    new_column = "active"
    info = conn.execute("PRAGMA table_info('subdomains')").fetchall()
    if not any(new_column in word for word in info):
        add_column = "ALTER TABLE subdomains ADD COLUMN active integer default 1"
        conn.execute(add_column)
        conn.commit()
        logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : Database updated")
