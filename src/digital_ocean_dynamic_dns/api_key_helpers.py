# digital-ocean-dynamic-dns
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
#   and the digital-ocean-dynamic-dns contributors

import os

from rich import print


class NoAPIKeyError(Exception):
    """Raised when the user tries to do anything without first configuring an API key."""


def get_api() -> str:
    """Retrieve the Digital Ocean API Token.

    There are currently two available sources for configuring the
      Digital Ocean API Token.

    The list below is ordered by precedence (i.e. the first value found is used):
        1. Environment variable DIGITALOCEAN_TOKEN
            - This is name that the official Digital Ocean Python
                library [pydo](https://pydo.readthedocs.io/en/latest/) uses.
        2. The value stored in the database.
    """
    api_token = os.environ.get("DIGITALOCEAN_TOKEN")
    if api_token is None:
        print(
            "[red]Error:[/red] Missing APIkey. "
            "Please set the DIGITALOCEAN_TOKEN environment variable!"
        )
        raise NoAPIKeyError(
            "Missing API key. Please set the DIGITALOCEAN_TOKEN environment variable!"
        )

    return api_token
