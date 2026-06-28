# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Utilities for displaying the DDNS update log file."""

from argparse import Namespace

from rich import print as rprint

from . import constants


def show_log(_args: Namespace) -> None:
    """Display the content of the log file.

    Args:
        _args: Parsed command-line arguments. Unused; kept for API consistency
            with other subcommand handlers.
    """
    with constants.logfile.open() as log_file:
        content = log_file.read()
        rprint(content)
