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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

from argparse import Namespace

from . import constants, domains, subdomains
from .database import connect_database

conn = connect_database(constants.database_path)


def manage(args: Namespace):
    """Martialing function for manage subparser."""

    # No matter what other options, always ensure the domain is managed.
    domains.manage_domain(args.domain)

    if args.subdomain is None:
        # usage do_ddns manage --domain example.com
        # I.e. importing all existing A records for example.com.
        domains.manage_all_existing_A_records(domain=args.domain)
    else:
        # usage do_ddns manage --domain example.com --subdomain www
        # I.e. configuring a single sub-domain to manage A records for.
        subdomains.manage_subdomain(subdomain=args.subdomain, domain=args.domain)
