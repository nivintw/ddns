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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors

"""The constants.py module contains some constants related to local configuration / data storage."""

from pathlib import Path

import pytest
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from ddns_digital_ocean import constants


class TestAppDataHome:
    """Tests related to setting the app data home.

    Supported platforms:
      - Linux
      - Macos
    Not Supported Yet:
      - Windows
      - Anything else.

    Determined by platform.system()
    """

    @pytest.mark.parametrize(
        "system_value",
        [
            pytest.param("Linux", id="linux"),
            pytest.param("Darwin", id="darwin"),
        ],
    )
    def test_XDG_DATA_HOME_set(
        self,
        monkeypatch: MonkeyPatch,
        mocker: MockerFixture,
        system_value,
    ):
        """If XDG_DATA_HOME is set, use that value as the user-specific data home."""
        EXPECTED_DATA_HOME = "/sentinel-data-home"
        mocked_platform = mocker.patch.object(constants.platform, "system")
        mocked_platform.return_value = system_value
        monkeypatch.setenv("XDG_DATA_HOME", EXPECTED_DATA_HOME)

        data_home = constants.set_app_data_home()
        assert data_home == Path(EXPECTED_DATA_HOME)

    @pytest.mark.parametrize(
        "system_value",
        [
            pytest.param("Linux", id="linux"),
            pytest.param("Darwin", id="darwin"),
        ],
    )
    def test_default_data_home_dir(
        self,
        monkeypatch: MonkeyPatch,
        mocker: MockerFixture,
        system_value,
    ):
        """Validate default data home when XDG_DATA_HOME is not set."""
        EXPECTED_DATA_HOME = Path.home() / ".local" / "share"
        mocked_platform = mocker.patch.object(constants.platform, "system")
        mocked_platform.return_value = system_value
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)

        data_home = constants.set_app_data_home()
        assert data_home == Path(EXPECTED_DATA_HOME)

    @pytest.mark.parametrize(
        "system_value, err_msg",
        [
            pytest.param("Windows", "Windows not yet supported.", id="Windows"),
            pytest.param(
                "Other-Unknown", "Unknown platform; file a ticket to discuss support.", id="Unknown"
            ),
        ],
    )
    def test_unsupported_platforms_raise(
        self,
        system_value: str,
        err_msg: str,
        mocker: MockerFixture,
    ):
        """No support for windows or others."""
        mocked_platform = mocker.patch.object(constants.platform, "system")
        mocked_platform.return_value = system_value

        with pytest.raises(RuntimeError, match=err_msg):
            constants.set_app_data_home()
