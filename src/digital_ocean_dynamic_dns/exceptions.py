# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Custom exceptions for digital-ocean-dynamic-dns."""


class NonSimpleDomainNameError(Exception):
    """Supported domain names must be in a simple format.

    i.e. ascii_letters + "." + digits + "-" + "@"
    """
