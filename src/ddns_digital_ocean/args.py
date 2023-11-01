import argparse


def setup_argparse():
    parser = argparse.ArgumentParser(
        prog="do_ddns",
        description="Application to use domains from DigitalOcean account as dynamic "
        "DNS domain(s).\nThe app only supports IP4. IPv6 is planned for a later release!"
        "\nYou'll always find the latest version on https://github.com/nivintw/ddns\n\n"
        "For bugs, suggestions, pull requests visit https://github.com/nivintw/ddns/issues\n\n"
        "Forked with appreciation from https://gitlab.pm/rune/ddns\n\n",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Making Selfhosting easier...",
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
        "-e",
        "--edit",
        help="Changes domain from active to inactive or the other way around...",
        required=False,
        nargs=1,
        metavar=("test.example.com"),
        action="append",
    )

    subparsers = parser.add_subparsers()

    parser_ip_server = subparsers.add_parser(
        name="update_ip_lookup",
        aliases=["ip_lookup"],
        help=("Update the service/server used to lookup your public IP address."),
    )
    parser_ip_server.add_argument(
        "--ip-lookup-url",
        default="https://www.ipify.org",
        help=(
            "The URL if the server to use for obtaining your current IP address. "
            "Default: %(default)s"
        ),
    )
    parser_ip_server.add_argument(
        "--ip-mode",
        choices=["4", "6"],
        default="4",
        help=("IPv4 or IPv6. Which IP address to update. Default: %(default)s"),
    )

    parser_api_key = subparsers.add_parser(
        name="api_key",
        aliases=["set_api_key"],
        help="Add/Change the Digital Ocean API Key.",
    )
    parser_api_key.add_argument("api_key", help="The API key value", type=str)

    return parser
