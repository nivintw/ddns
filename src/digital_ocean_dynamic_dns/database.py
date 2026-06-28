# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Database connection and schema initialization for Digital Ocean Dynamic DNS."""

import logging
import sqlite3
import time
from pathlib import Path
from sqlite3 import Error

from rich import print as rprint

logger = logging.getLogger(__name__)


def connect_database(database_path: Path) -> sqlite3.Connection:
    """Connect to the SQLite database and initialize the schema.

    Args:
        database_path: Path to the SQLite database file.

    Returns:
        An open SQLite connection with the schema initialized.

    Raises:
        Error: If the database connection fails.
    """
    conn = None

    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
    except Error as e:
        logger.exception("Error at %s", time.strftime("%Y-%m-%d %H:%M"))
        rprint(e)
        raise
    else:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS ipservers (
                id integer NOT NULL PRIMARY KEY,
                URL text NOT NULL UNIQUE,
                ip_version text NOT NULL
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS domains (
                id integer PRIMARY KEY,
                name text NOT NULL UNIQUE,
                cataloged text NOT NULL,
                managed integer default 1,
                last_managed text default 'N/A'
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS subdomains (
                domain_record_id integer PRIMARY KEY,
                main_id integer NOT NULL REFERENCES domains (id) ON DELETE RESTRICT,
                name text NOT NULL,
                current_ip4 text NOT NULL,
                current_ip6 text NULL,
                cataloged text NOT NULL,
                managed integer default 1,
                last_checked text default 'N/A',
                last_updated text default 'N/A'
            )"""
        )

        return conn
