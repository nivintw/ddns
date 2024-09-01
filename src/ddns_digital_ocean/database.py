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
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech>
# and the ddns-digital-ocean contributors

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
                ip4_server text NOT NULL,
                ip6_server text
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS domains (
                id integer PRIMARY KEY,
                name text NOT NULL,
                cataloged text NOT NULL,
                managed integer default 1,
                last_managed text default 'N/A'
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS subdomains (
                id integer PRIMARY KEY,
                main_id integer NOT NULL,
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
