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
# Copyright 2024 - 2024, Tyler Nivin <tyler@nivin.tech>
#   and the ddns-digital-ocean contributors


class TestManageSubdomain:
    """Users can register subdomains to have dynamic DNS A records.

    This is done via the manage_subdomain interface.
    If they supply a subdomain with a parent domain that is not currently managed
      we handle the details of ensuring the domain is managed for them.
    However, this is done external to the manage_subdomain call, which assumes that the
      domain specified has been registered already.
    """

    # TODO: add these tests.

    def test_subdomain_results_in_a_records(
        self,
        mock_db_for_test,
        mocker,
    ):
        """Provided valid arguments, manage_subdomain results in A records being created."""
        ...
