# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Smoke test — replace with real tests."""

from digital_ocean_dynamic_dns import __version__


def test_version() -> None:
    """The package exposes a version string."""
    assert isinstance(__version__, str)
