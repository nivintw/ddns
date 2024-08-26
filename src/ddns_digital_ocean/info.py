from argparse import Namespace

from rich import print

from . import __version__, constants
from .api_key_helpers import NoAPIKeyError, get_api
from .database import connect_database

conn = connect_database(constants.database_path)


def show_current_info(args: Namespace):
    try:
        # NOTE: this is the rare (only?) time where
        # there not being an API key yet is not an error / is ok.
        API = get_api()
    except NoAPIKeyError:
        API = "[red]Error:[/red] API key not stored in DB"
    if args.show_api_key is not True:
        API = "*" * len(API)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(ip4_server) FROM ipservers")
    count = cursor.fetchone()[0]
    if count == 0:
        ip4server = "[red]None Configured[/red]"
        ip6server = "[red]None Configured[/red]"
    else:
        cursor.execute("SELECT * FROM ipservers")
        ipservers = cursor.fetchall()
        ip4server = ipservers[0][1]
        ip6server = ipservers[0][2]

    cursor.execute("SELECT COUNT(*) FROM domains")
    topdomains = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subdomains")
    subdomains = cursor.fetchone()[0]

    print("\n[b]ddns[/b] - a DigitalOcean dynamic DNS solution.")
    print("===================================================")
    print(f"API key 		: [b]{API}[/b]")
    print(f"IP v4 resolver 		: [b]{ip4server}[/b]")
    print(f"IP v6 resolver 		: [b]{ip6server}[/b]")
    print(f"Logfile 		: [b]{constants.logfile}[/b]")
    print(f"Top-Level domains 	: [b]{topdomains}[/b]")
    print(f"Sub-domains 		: [b]{subdomains}[/b]")
    print("")
    print(f"App version 	: [b]{__version__}[/b] (https://github.com/nivintw/ddns)")
    print("")
    print("[i]IPv6 is not supported and not listed here.[/i]")
