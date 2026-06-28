# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

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
        API = "[red]Error:[/red] Unable to read the API Key. Set DIGITALOCEAN_TOKEN env variable."
    else:
        # API key was found.
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
