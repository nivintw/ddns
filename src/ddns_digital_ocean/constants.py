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
# Copyright 2023 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

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
