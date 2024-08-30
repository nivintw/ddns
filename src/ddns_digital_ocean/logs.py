# ddns-digital-ocean
# Copyright (C) 2023  Tyler Nivin <tyler@nivin.tech>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech> and the ddns-digital-ocean contributors

from argparse import Namespace

from rich import print

from . import constants


def show_log(args: Namespace):
    # TODO: refactor this...
    # this logic seems ... odd?
    # NOTE: right now, intentionally don't use args here.
    # but for consistencies sake, just keep the API the same.
    with constants.logfile.open() as log_file:
        content = log_file.read()
        print(content)
