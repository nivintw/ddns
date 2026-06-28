# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Digital Ocean Dynamic DNS."""

from importlib.metadata import PackageNotFoundError, version

# Single source of truth: the installed distribution's version. release-please bumps the
# version in pyproject.toml, which is what the built/installed package metadata reflects,
# so this never drifts the way a hand-edited constant would. Fall back gracefully when the
# distribution isn't installed (e.g. running from a bare source checkout) so importing the
# package never hard-fails.
try:
    __version__ = version("digital-ocean-dynamic-dns")
except PackageNotFoundError:  # pragma: no cover - only hit when running uninstalled
    __version__ = "0.0.0+unknown"
