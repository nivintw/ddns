# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Digital Ocean Dynamic DNS."""

from importlib.metadata import version

# Single source of truth: the installed distribution's version. release-please bumps the
# version in pyproject.toml, which is what the built/installed package metadata reflects,
# so this never drifts the way a hand-edited constant would.
__version__ = version("digital-ocean-dynamic-dns")
