import json
import logging
import time
import urllib.request
from string import ascii_letters, digits

import requests
from rich import print

from . import __version__, constants
from . import subdomains as sd
from .api_key_helpers import NoAPIKeyError, get_api
from .args import setup_argparse
from .database import connect_database, updatedb
from .ip import get_ip

logging.basicConfig(filename=constants.logfile, level=logging.INFO, format="%(message)s")

app_version = __version__

conn = connect_database(constants.database_path)


def add_domain(domain):
    apikey = get_api()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (domain,))
    count = cursor.fetchone()[0]
    if count != 0:
        print(f"[red]Error:[/red] Domain name ({domain}) already in database!")
        return

    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
    }
    response = requests.get(
        "https://api.digitalocean.com/v2/domains/" + domain,
        headers=headers,
        timeout=45,
    )
    response_data = response.json()

    if response.status_code == 401:
        print(
            "[red]Error: [/red]"
            "The api key that is configured resulted in an unauthorized response.\n"
            "Please configure a valid Digital Ocean API key to use."
            f"Response: {response_data}"
        )
        return
    elif response.status_code == 404:
        print(
            "[red]Error: [/red]The domain does not exist in your DigitalOcean account.\n"
            "Please add the domain from your control panel "
            "[b]https://cloud.digitalocean.com/networking/domains/[/b]"
        )
        return
    elif response.status_code == 429:
        print("[red]Error: [/red]API Rate limit exceeded. Please try again later.")
        return
    elif response.status_code == 500:
        print(
            "[red]Error: [/red]"
            "Unexpected Internal Server Error Response from DigitalOcean. "
            "Please try again later."
        )
        return
    elif response.status_code != requests.codes.ok:
        print(
            "[red]Error: [/red]"
            "Completely unexpected error response from Digital Ocean."
            "This is neat. If you see this more than once, open a ticket."
            f"Response: {response_data}"
        )
        return

    cursor.execute(
        "INSERT INTO domains values(?,?)",
        (
            None,
            domain,
        ),
    )
    print(f"The domain [b]{domain}[/b] has been added to the DB")
    logging.info(time.strftime("%Y-%m-%d %H:%M") + f" - Info : Domain {domain} added")
    conn.commit()


def show_all_top_domains():
    cursor = conn.cursor()
    apikey = get_api()

    req = urllib.request.Request("https://api.digitalocean.com/v2/domains/?per_page=200")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + apikey)
    current = urllib.request.urlopen(req)  # noqa: S310
    remote = current.read().decode("utf-8")
    remoteData = json.loads(remote)
    print("Domains in database are marked with a [*]")
    print("================================================")
    for k in remoteData["domains"]:
        cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (k["name"],))
        count = cursor.fetchone()[0]
        if count != 0:
            print("Name : [bold]" + k["name"] + " [*][/bold]")
        else:
            print("Name : " + k["name"])


def domaininfo(domain):
    local_ip = get_ip()
    cursor = conn.cursor()
    if set(domain).difference(ascii_letters + "." + digits + "@" + "-"):
        print(
            "[red]Error:[/red]. Give the domain name in simple form "
            "e.g. [bold]test.domain.com[/bold]"
        )
        return

    parts = domain.split(".")
    if len(parts) > 3:
        top = parts[1] + "." + parts[2] + "." + parts[3]
    else:
        top = parts[1] + "." + parts[2]
    cursor.execute("SELECT id FROM domains WHERE name like ?", (top,))
    domain_id = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM subdomains WHERE main_id like ?", (domain_id,))
    domains = cursor.fetchall()
    local_ip = f"[red]{local_ip}[/red]" if local_ip != domains[0][3] else local_ip

    print(
        f"The domain [bold]{domain}[/bold] has the IP [bold]{domains[0][3]}[/bold]. "
        f"Your public IP is [bold]{local_ip}[/bold]."
    )


def show_current_info():
    try:
        # NOTE: this is the rare (only?) time where
        # there not being an API key yet is not an error / is ok.
        API = get_api()
    except NoAPIKeyError:
        API = "[red]Error:[/red] API key not stored in DB"

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
    print(f"API key 	: [b]{API}[/b]")
    print(f"IP v4 resolver 	: [b]{ip4server}[/b]")
    print(f"IP v6 resolver 	: [b]{ip6server}[/b]")
    print(f"Logfile 	: [b]{constants.logfile}[/b]")
    print(f"Top domains 	: [b]{topdomains}[/b]")
    print(f"sub domains 	: [b]{subdomains}[/b]")
    print("")
    print(f"App version 	: [b]{app_version}[/b] (https://github.com/nivintw/ddns)")
    print("")
    print("[i]IPv6 is not supported and not listed here.[/i]")


def show_log():
    # TODO: refactor this...
    # this logic seems ... odd?
    with open(constants.logfile) as log_file:
        content = log_file.read()
        print(content)


def run():
    # Commandline arguments
    updatedb()

    parser = setup_argparse()

    args_raw = parser.parse_args()
    args = vars(args_raw)

    # TODO: update args to support multiple domains at the same time.
    # Right now, argparse has been updated to support multiple values but we haven't updated
    # this section to make multiple args actually work.

    if args["list"]:
        sd.list_sub_domains(args["list"][0][0])
    elif args["domains"]:
        show_all_top_domains()
    elif args["serverdomains"]:
        sd.list_do_sub_domains(args["serverdomains"][0][0])
    elif args["current"]:
        domaininfo(args["current"][0][0])
    elif top_level_domains := args["top"]:
        for tld in top_level_domains:
            add_domain(tld)
    elif args["sub"]:
        sd.add_subdomain(args["sub"][0][0])
    elif args["version"]:
        show_current_info()
    elif args["log"]:
        show_log()
    elif args_raw.subparser_name in [
        "ip_lookup_config",
        "api_key",
        "update_ips",
    ]:
        # NOTE: these subparsers have been configured.
        # eventually, all options will be handled similarly.
        args_raw.func(args_raw)
    elif args["remove"]:
        sd.remove_subdomain(args["remove"][0][0])
    elif args["edit"]:
        sd.edit_subdomain(args["edit"][0][0])
    elif args["local"]:
        sd.local_add_subdomain(args["local"][0][0], args["local"][0][1])


if __name__ == "__main__":
    run()
