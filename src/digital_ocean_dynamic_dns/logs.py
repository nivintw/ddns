# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Utilities for displaying the DDNS update log file."""

from argparse import Namespace

from rich import print as rich_print

from . import constants


def show_log(_args: Namespace) -> None:
    """Display the content of the log file.

    Args:
        _args: Parsed command-line arguments. Unused; kept for API consistency
            with other subcommand handlers.
    """
    # Args is intentionally unused; the API signature is kept consistent with
    # other subcommand handlers that do receive and use args.
    with constants.logfile.open() as log_file:
        content = log_file.read()
        rich_print(content)
