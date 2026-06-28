# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Application-level constants and filesystem paths for digital-ocean-dynamic-dns."""

import os
import platform
from pathlib import Path


def set_app_data_home() -> Path:
    """Determine the application data home directory based on the current platform.

    Follows the XDG Base Directory specification on Linux and macOS.

    Returns:
        The resolved application data home directory.

    Raises:
        RuntimeError: If running on Windows or an unrecognized platform.
    """
    match platform.system():
        case "Linux" | "Darwin":
            # Linux or macOS.
            # Technically macOS wants ~/Library/Application Support/...
            # but XDG conventions are preferred here.

            # Use XDG_DATA_HOME if it's defined,
            # else fall back to ~/.local/share per XDG spec.
            # Ref: https://specifications.freedesktop.org/basedir-spec/latest/index.html
            data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        case "Windows":
            # Windows is not yet supported; contributions welcome.
            msg = "Windows not yet supported."
            raise RuntimeError(msg)
        case _:
            msg = "Unknown platform; file a ticket to discuss support."
            raise RuntimeError(msg)
    return data_home


app_data_home = set_app_data_home() / "tech.nivin.digital-ocean-dynamic-dns"
app_data_home.mkdir(parents=True, exist_ok=True)

database_path = app_data_home.joinpath("do_ddns.db")
logfile = app_data_home.joinpath("do_ddns.log")
