# ddns-digital-ocean
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
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

import logging
import sqlite3
import time
from pathlib import Path
from sqlite3 import Error

from rich import print


def connect_database(database_path: Path):
    conn = None

    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
    except Error as e:
        logging.error(time.strftime("%Y-%m-%d %H:%M") + " - Error : " + str(e))
        print(e)
        raise
    else:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS apikey (
                id integer NOT NULL PRIMARY KEY,
                key text NOT NULL,
                last_updated text default 'N/A'
            )"""
        )
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


# TODO: Decide if I want to implement this.
# def purge_database(database_path: Path):
#     """Delete all local database files.

#     This rarely-used utility should only be used if you need to cleanup a prior database.
#     """

#     for root, dirs, files in database_path.walk(top_down=False):
#         for name in files:
#             (root / name).unlink()
#         for name in dirs:
#             (root / name).rmdir()

#     database_path.rmdir()
