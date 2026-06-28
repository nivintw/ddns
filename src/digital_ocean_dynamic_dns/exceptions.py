# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

class NonSimpleDomainNameError(Exception):
    """Supported domain names must be in a simple format.
    i.e. ascii_letters + "." + digits + "-" + "@"
    """
