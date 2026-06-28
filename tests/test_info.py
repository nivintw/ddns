# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT
"""Tests for the show-info command output."""

import pytest

from digital_ocean_dynamic_dns import args


class TestShowInfo:
    """Ensure ability to show info about the current configuration."""

    def test_user_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """User output is provided.

        For now, keep this test simple.
        I'm just checking that output _is_ created, and not
        testing the correctness of the output...
        The code that produces the output is _extremely_ simple.

        """
        parser = args.setup_argparse()
        test_args = parser.parse_args(["show-info"])

        test_args.func(test_args)
        capd_output = " ".join(capsys.readouterr().out.split())
        assert "do_ddns - an open-source dynamic DNS solution for DigitalOcean." in capd_output
        assert "API key" in capd_output
        # note... not testing all fields here intentionally.
