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

from argparse import Namespace

from rich.console import Console
from rich.table import Table

from . import __version__, constants
from .api_key_helpers import NoAPIKeyError, get_api
from .database import connect_database

conn = connect_database(constants.database_path)


def show_current_info(args: Namespace):
    console = Console()
    grid = Table(
        title="[b]do_ddns[/b] - an open-source dynamic DNS solution for DigitalOcean.",
        show_header=False,
        box=None,
        highlight=True,
    )
    grid.add_column()
    grid.add_column()

    try:
        # NOTE: this is the rare (only?) time where
        # there not being an API key yet is not an error / is ok.
        API = get_api()
    except NoAPIKeyError:
        API = "[red]Error:[/red] Unable to source API Key."
    if args.show_api_key is not True:
        API = "[green]Configured[/green]"

    cursor = conn.cursor()
    row = cursor.execute("SELECT URL FROM ipservers where ip_version = '4'").fetchone()
    ip4server = "[red]None Configured[/red]" if row is None else row["URL"]

    cursor.execute("SELECT COUNT(*) FROM domains")
    topdomains = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subdomains")
    subdomains = cursor.fetchone()[0]

    grid.add_row("API key", API)
    grid.add_row("IPv4 resolver", f"{ip4server}")
    grid.add_row("Log file", f"{constants.logfile}")
    grid.add_row("Domains", f"{topdomains}")
    grid.add_row('Sub-domains ("A" records)', f"{subdomains}")
    grid.add_row("App version", f"{__version__} (https://github.com/nivintw/ddns)")
    console.print(grid)
