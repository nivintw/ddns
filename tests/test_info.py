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

from pytest import CaptureFixture

from digital_ocean_dynamic_dns import args


class TestShowInfo:
    """Ensure ability to show info about the current configuration."""

    def test_user_output(
        self,
        capsys: CaptureFixture[str],
    ):
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
