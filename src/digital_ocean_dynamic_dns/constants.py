# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

import os
import platform
from pathlib import Path


def set_app_data_home():
    match platform.system():
        case "Linux" | "Darwin":
            # Linux or Macos.
            # Technically... Macos wants us to use ~/Library/Application Support/...
            # But, i'm not alone in saying... nah thanks.

            # Use XDG_DATA_HOME if it's defined,
            # else fall back to ~/.local/share per XDG spec.
            # Ref: https://specifications.freedesktop.org/basedir-spec/latest/index.html
            data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        case "Windows":
            # TODO: Phone a friend about Windows...
            raise RuntimeError("Windows not yet supported.")
        case _:
            raise RuntimeError("Unknown platform; file a ticket to discuss support.")
    return data_home


app_data_home = set_app_data_home() / "tech.nivin.digital-ocean-dynamic-dns"
app_data_home.mkdir(parents=True, exist_ok=True)

database_path = app_data_home.joinpath("do_ddns.db")
logfile = app_data_home.joinpath("do_ddns.log")
