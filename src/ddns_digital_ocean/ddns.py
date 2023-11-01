import json
import logging
import time
import urllib.request
from string import ascii_letters, digits

import requests
from rich import print

from . import __version__, constants
from . import subdomains as sd
from .api_key_helpers import api, get_api
from .args import setup_argparse
from .database import connect_database, updatedb
from .ip import get_ip, updateip

logging.basicConfig(
    filename=constants.logfile, level=logging.INFO, format="%(message)s"
)

app_version = __version__

conn = connect_database(constants.database_path)


def add_domain(domain):
    apikey = get_api()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM domains WHERE name like ?", (domain,))
    count = cursor.fetchone()[0]
    if count != 0:
        print("[red]Error:[/red] Domain name (%s) already in database!" % (domain))
    else:
        if apikey != None:
            headers = {
                "Authorization": "Bearer " + apikey,
                "Content-Type": "application/json",
            }
            response = requests.get(
                "https://api.digitalocean.com/v2/domains/" + domain, headers=headers
            )
            response_data = response.json()

            if "id" in response_data:
                print(
                    "[red]Error: [/red]The domain does not exist in your DigitalOcean account.\nPlease add the domain from your control panel [b]https://cloud.digitalocean.com/networking/domains/[/b]"
                )
            else:
                cursor.execute(
                    "INSERT INTO domains values(?,?)",
                    (
                        None,
                        domain,
                    ),
                )
                print("The domain [b]%s[/b] has been added to the DB" % (domain))
                logging.info(
                    time.strftime("%Y-%m-%d %H:%M")
                    + " - Info : Domain %s added" % (domain)
                )
                conn.commit()


def show_all_top_domains():
    cursor = conn.cursor()
    apikey = get_api()
    if apikey is not None:
        req = urllib.request.Request(
            "https://api.digitalocean.com/v2/domains/?per_page=200"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer " + apikey)
        current = urllib.request.urlopen(req)
        remote = current.read().decode("utf-8")
        remoteData = json.loads(remote)
        print("Domains in database are marked with a [*]")
        print("================================================")
        for k in remoteData["domains"]:
            cursor.execute(
                "SELECT COUNT(*) FROM domains WHERE name like ?", (k["name"],)
            )
            count = cursor.fetchone()[0]
            if count != 0:
                print("Name : [bold]" + k["name"] + " [*][/bold]")
            else:
                print("Name : " + k["name"])

    else:
        print("[red]Error:[/red] Missing APIkey. Please add one!")


def domaininfo(domain):
    apikey = get_api()
    local_ip = get_ip()
    cursor = conn.cursor()
    if set(domain).difference(ascii_letters + "." + digits + "@" + "-"):
        print(
            "[red]Error:[/red]. Give the domain name in simple form e.g. [bold]test.domain.com[/bold]"
        )
    else:
        parts = domain.split(".")
        if len(parts) > 3:
            top = parts[1] + "." + parts[2] + "." + parts[3]
            sub = parts[0]
        else:
            sub = parts[0]
            top = parts[1] + "." + parts[2]
        cursor.execute("SELECT id FROM domains WHERE name like ?", (top,))
        domainid = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM subdomains WHERE main_id like ?", (domainid,))
        domains = cursor.fetchall()
        if local_ip != domains[0][3]:
            localip = "[red]%s[/red]" % (local_ip)
        else:
            localip = local_ip
        print(
            "The domain [bold]%s[/bold] has the IP [bold]%s[/bold]. Your public IP is [bold]%s[/bold]"
            % (domain, domains[0][3], localip)
        )


def show_current_info():
    ipserver = None
    API = get_api()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(ip4_server) FROM ipservers")
    count = cursor.fetchone()[0]
    if count == 0:
        ipserver = "[red]Error:[/red] No IP resolvers in DB"
    else:
        cursor.execute("SELECT * FROM ipservers")
        ipservers = cursor.fetchall()
        ip4server = ipservers[0][1]
        ip6server = ipservers[0][2]

    if API is None:
        API = "[red]Error:[/red] API key not stored in DB"

    cursor.execute("SELECT COUNT(*) FROM domains")
    topdomains = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subdomains")
    subdomains = cursor.fetchone()[0]

    print("\n[b]ddns[/b] - a DigitalOcean dynamic DNS solution.")
    print("===================================================")
    print("API key 	: [b]%s[/b]" % (API))
    print("IP v4 resolver 	: [b]%s[/b]" % (ip4server))
    print("IP v6 resolver 	: [b]%s[/b]" % (ip6server))
    print("Logfile 	: [b]%s[/b]" % (constants.logfile))
    print("Top domains 	: [b]%s[/b]" % (topdomains))
    print("sub domains 	: [b]%s[/b]" % (subdomains))
    print("")
    print("App version 	: [b]%s[/b] (https://gitlab.pm/rune/ddns)" % (app_version))
    print("")
    print("[i]IPv6 is not supported and not listed here.[/i]")


def ip_server(ipserver, ip_type):
    cursor = conn.cursor()
    if ip_type == "4":
        cursor.execute("SELECT COUNT(ip4_server) FROM ipservers")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                "INSERT INTO ipservers values(?,?,?)", (None, ipserver, None)
            )
            conn.commit()
            print("New IP resolver (%s) for ipv%s added." % (ipserver, ip_type))
        else:
            cursor.execute(
                "UPDATE ipservers SET ip4_server = ? WHERE id = 1", (ipserver,)
            )
            print("IP resolver (%s) for ipv%s updated." % (ipserver, ip_type))
            logging.info(
                time.strftime("%Y-%m-%d %H:%M")
                + " - Info : IP resolver (%s) for ipv%s updated." % (ipserver, ip_type)
            )
            conn.commit()
    elif ip_type == "6":
        cursor.execute("SELECT COUNT(ip6_server) FROM ipservers")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                "INSERT INTO ipservers values(?,?,?)", (None, None, ipserver)
            )
            conn.commit()
            print(
                "New IP resolver (%s) for ipv%s added. \n\r This IP version is not supported."
                % (ipserver, ip_type)
            )
        else:
            cursor.execute(
                "UPDATE ipservers SET ip6_server = ? WHERE id = 1", (ipserver,)
            )
            print(
                "IP resolver (%s) for ipv%s updated. \n\r This IP version is not supported."
                % (ipserver, ip_type)
            )
            logging.info(
                time.strftime("%Y-%m-%d %H:%M")
                + " - Info : IP resolver (%s) for ipv%s updated." % (ipserver, ip_type)
            )
            conn.commit()


def show_log():
    log_file = open(constants.logfile, "r")
    content = log_file.read()
    print(content)
    log_file.close()


def run():
    # Commandline arguments
    updatedb()

    parser = setup_argparse()

    args = vars(parser.parse_args())

    if args["list"]:
        sd.list_sub_domains(args["list"][0][0])
    elif args["domains"]:
        show_all_top_domains()
    elif args["serverdomains"]:
        sd.list_do_sub_domains(args["serverdomains"][0][0])
    elif args["current"]:
        domaininfo(args["current"][0][0])
    elif args["top"]:
        add_domain(args["top"][0][0])
    elif args["sub"]:
        sd.add_subdomain(args["sub"][0][0])
    elif args["version"]:
        show_current_info()
    elif args["force"]:
        updateip(True)
    elif args["log"]:
        show_log()
    elif "ip_lookup_url" in args:
        ip_server(args["ip_lookup_url"], args["ip_mode"])
    elif "api_key" in args:
        api(args["api_key"])
    elif args["remove"]:
        sd.remove_subdomain(args["remove"][0][0])
    elif args["edit"]:
        sd.edit_subdomain(args["edit"][0][0])
    elif args["local"]:
        sd.local_add_subdomain(args["local"][0][0], args["local"][0][1])
    else:
        updateip(None)
