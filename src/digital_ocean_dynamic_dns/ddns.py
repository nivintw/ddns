# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Entry point for the digital-ocean-dynamic-dns CLI."""

import logging

from . import constants
from .args import setup_argparse

logging.basicConfig(filename=constants.logfile, level=logging.INFO, format="%(message)s")


def run() -> None:
    """Parse CLI arguments and dispatch to the appropriate subcommand handler."""
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    run()
