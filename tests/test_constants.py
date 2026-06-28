# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""The constants.py module contains some constants related to local configuration / data storage."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from digital_ocean_dynamic_dns import constants


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
    def test_xdg_data_home_set(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
        system_value: str,
    ) -> None:
        """If XDG_DATA_HOME is set, use that value as the user-specific data home."""
        expected_data_home = "/sentinel-data-home"
        mocked_platform = mocker.patch.object(constants.platform, "system")
        mocked_platform.return_value = system_value
        monkeypatch.setenv("XDG_DATA_HOME", expected_data_home)

        data_home = constants.set_app_data_home()
        assert data_home == Path(expected_data_home)

    @pytest.mark.parametrize(
        "system_value",
        [
            pytest.param("Linux", id="linux"),
            pytest.param("Darwin", id="darwin"),
        ],
    )
    def test_default_data_home_dir(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
        system_value: str,
    ) -> None:
        """Validate default data home when XDG_DATA_HOME is not set."""
        expected_data_home = Path.home() / ".local" / "share"
        mocked_platform = mocker.patch.object(constants.platform, "system")
        mocked_platform.return_value = system_value
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)

        data_home = constants.set_app_data_home()
        assert data_home == Path(expected_data_home)

    @pytest.mark.parametrize(
        ("system_value", "err_msg"),
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
    ) -> None:
        """No support for windows or others."""
        mocked_platform = mocker.patch.object(constants.platform, "system")
        mocked_platform.return_value = system_value

        with pytest.raises(RuntimeError, match=err_msg):
            constants.set_app_data_home()
