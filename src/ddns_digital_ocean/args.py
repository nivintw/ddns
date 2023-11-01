import argparse


def setup_argparse():
    parser = argparse.ArgumentParser(
        prog="ddns",
        description="Application to use domains from DigitalOcean account as dynamic "
        "DNS domain(s).\nThe app only supports IP4. IPv6 is planned for a later release!"
        "\nYou'll always find the latest version on https://gitlab.pm/rune/ddns\n\n"
        "For bugs, suggestions, pull requests visit https://gitlab.pm/rune/ddns/issues",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Making Selfhosting easier...",
    )

    parser.add_argument(
        "-a",
        "--api",
        help="Add/Change API key.\n\n",
        nargs=1,
        metavar=("APIkey"),
        required=False,
        action="append",
    )

    parser.add_argument(
        "-f",
        "--force",
        help="Force update of IP address for all domains.\n\n",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--list",
        help="List subdomains for supplied domain.\n\n",
        nargs=1,
        metavar=("domain"),
        required=False,
        action="append",
    )

    parser.add_argument(
        "-o",
        "--serverdomains",
        help="List subdomains for supplied domain not in ddns DB.\n\n",
        nargs=1,
        metavar=("domain"),
        required=False,
        action="append",
    )

    parser.add_argument(
        "-d",
        "--domains",
        help="List top domains in your DigitalOcean account.\n\n",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--current",
        help="List the current IP address for the sub-domain given\n\n",
        required=False,
        nargs=1,
        action="append",
    )

    parser.add_argument(
        "-t",
        "--top",
        help="Add a new domain from your DigitalOcean account to use as a dynamic DNS domain\n\n",
        required=False,
        nargs=1,
        metavar=("domain"),
        action="append",
    )

    parser.add_argument(
        "-s",
        "--sub",
        help="Add a new subdomain to your DigitalOcean account and use as dynamic DNS.\n\n\n",
        required=False,
        nargs=1,
        metavar=("domain"),
        action="append",
    )

    parser.add_argument(
        "-k",
        "--local",
        help="Add an existing DigitalOcean subdomain to your ddns DB and use as dynamic DNS.\n\n",
        required=False,
        nargs=2,
        metavar=("domain", "domainid"),
        action="append",
    )

    parser.add_argument(
        "-r",
        "--remove",
        help="Remove a subdomain from your DigitalOcean account and ddns.\n\n",
        required=False,
        nargs=1,
        metavar=("domain"),
        action="append",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Show current version and config info\n\n",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "-q", "--log", help=argparse.SUPPRESS, required=False, action="store_true"
    )

    parser.add_argument(
        "-p",
        "--ipserver",
        help="Sets or updates IP server lookup to use. Indicate 4 or 6 for IP type.\n\n",
        required=False,
        nargs=2,
        metavar=("ip4.iurl.no", "4"),
        action="append",
    )

    parser.add_argument(
        "-e",
        "--edit",
        help="Changes domain from active to inactive or the other way around...",
        required=False,
        nargs=1,
        metavar=("test.example.com"),
        action="append",
    )

    return parser
