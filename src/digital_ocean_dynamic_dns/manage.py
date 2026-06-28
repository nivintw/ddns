# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

from argparse import Namespace

from . import constants, domains, subdomains
from .database import connect_database

conn = connect_database(constants.database_path)


def martial_manage(args: Namespace):
    """Martialing function for manage subparser."""
    # No matter what other options, always ensure the domain is managed.
    domains.manage_domain(args.domain)

    if args.list:
        subdomains.list_sub_domains(args.domain)
    elif args.subdomain is None:
        # usage do_ddns manage example.com
        # I.e. importing all existing A records for example.com.
        domains.manage_all_existing_a_records(domain=args.domain)
    else:
        # usage do_ddns manage example.com --subdomain www
        # I.e. configuring a single sub-domain to manage A records for.
        subdomains.manage_subdomain(subdomain=args.subdomain, domain=args.domain)


def martial_un_manage(args: Namespace):
    """Martialing function un-manage subparser."""
    if args.list:
        subdomains.list_sub_domains(args.domain)
    elif args.subdomain is None:
        # usage do_ddns un-manage example.com
        domains.un_manage_domain(domain=args.domain)
    else:
        # usage do_ddns un-manage example.com --subdomain www
        subdomains.un_manage_subdomain(subdomain=args.subdomain, domain=args.domain)
