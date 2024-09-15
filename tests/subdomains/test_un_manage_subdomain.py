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

import datetime as dt
from sqlite3 import Connection

import pytest
from pytest import CaptureFixture

from ddns_digital_ocean import subdomains

pytestmark = pytest.mark.usefixtures("mocked_responses")


@pytest.mark.parametrize(
    "expected_subdomain, expected_domain",
    [
        pytest.param("support.example.com", "example.com", id="full-sub-domain"),
        pytest.param(
            "@",
            "example.com",
            id="short-sub-domain",
        ),
    ],
)
def test_top_domain_not_managed(
    capsys: CaptureFixture[str],
    expected_domain,
    expected_subdomain,
):
    """un_manage_subdomain raises TopDomainNotManagedError if the top domain is not managed.
    un_manage_subdomain() assumes the top domain is already being managed.
    """

    with pytest.raises(subdomains.TopDomainNotManagedError):
        subdomains.un_manage_subdomain(subdomain=expected_subdomain, domain=expected_domain)

    # Validate: We provide the user with some output, should we somehow reach this invalid state.
    capd_err_out = capsys.readouterr()
    assert f"Error: {expected_domain} is not a managed domain. " in capd_err_out.out


@pytest.mark.parametrize(
    "expected_subdomain, expected_domain",
    [
        pytest.param("support.example.com", "example.com", id="full-sub-domain"),
        pytest.param(
            "@",
            "example.com",
            id="short-sub-domain",
        ),
    ],
)
def test_side_effects(
    mock_db_for_test: Connection,
    capsys: CaptureFixture[str],
    expected_subdomain: str,
    expected_domain: str,
):
    """
    Expected side effects:
        1. subdomain marked as un-managed in database.
        2. User-facing output is provided.
    """
    # Arrange the create_A_record mock.
    EXPECTED_DOMAIN_RECORD_ID = 1001
    EXPECTED_A_RECORD_NAME = expected_subdomain.removesuffix("." + expected_domain)
    EXPECTED_IP4_ADDRESS = "127.0.0.1"

    # Arrange: Insert EXPECTED_DOMAIN into the db
    # as a managed domain.
    with mock_db_for_test:
        update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        mock_db_for_test.execute(
            "INSERT INTO domains(name, cataloged, last_managed) "
            " values(:name, :cataloged, :last_managed)",
            {
                "name": expected_domain,
                "cataloged": update_datetime,
                "last_managed": update_datetime,
            },
        )
        # Arrange: Insert EXPECTED_SUBDOMAIN into the db
        # as a managed subdomain.
        mock_db_for_test.execute(
            "INSERT INTO subdomains("
            "   domain_record_id,"
            "   main_id,"
            "   name,"
            "   current_ip4,"
            "   cataloged,"
            "   last_checked,"
            "   last_updated,"
            "   managed"
            ") values("
            "   :domain_record_id,"
            "   :main_id,"
            "   :name,"
            "   :current_ip4,"
            "   :cataloged,"
            "   :last_checked,"
            "   :last_updated,"
            "   1"
            ")",
            {
                "domain_record_id": EXPECTED_DOMAIN_RECORD_ID,
                "main_id": 1,  # expected id from domains.id
                "name": EXPECTED_A_RECORD_NAME,
                "current_ip4": EXPECTED_IP4_ADDRESS,
                "cataloged": update_datetime,
                "last_checked": update_datetime,
                "last_updated": update_datetime,
            },
        )

    subdomains.un_manage_subdomain(subdomain=expected_subdomain, domain=expected_domain)

    # Validate the subdomain was added to the database.
    row = mock_db_for_test.execute(
        "SELECT "
        "   domain_record_id,"
        "   main_id,"
        "   name,"
        "   current_ip4,"
        "   cataloged,"
        "   last_checked,"
        "   last_updated,"
        "   managed "
        "from subdomains "
        "WHERE "
        "name = :name",
        {"name": EXPECTED_A_RECORD_NAME},
    ).fetchone()
    assert row is not None  # triggered when no match / no insert.

    # Validate: inserted values.
    assert row["current_ip4"] == EXPECTED_IP4_ADDRESS
    assert row["domain_record_id"] == EXPECTED_DOMAIN_RECORD_ID
    assert dt.datetime.strptime(row["cataloged"], "%Y-%m-%d %H:%M") <= dt.datetime.now()
    assert dt.datetime.strptime(row["last_checked"], "%Y-%m-%d %H:%M") <= dt.datetime.now()
    assert dt.datetime.strptime(row["last_updated"], "%Y-%m-%d %H:%M") <= dt.datetime.now()
    assert row["main_id"] == 1  # expected id from domains.id
    assert row["managed"] == 0

    # Validate user output
    captured_out = capsys.readouterr().out
    captured_out = " ".join(captured_out.split())
    assert (
        f"{EXPECTED_A_RECORD_NAME} for domain {expected_domain}"
        " is no longer being managed by digital-ocean-dynamic-dns!" in captured_out
    )


@pytest.mark.parametrize(
    "expected_subdomain, expected_domain",
    [
        pytest.param("support.example.com", "example.com", id="full-sub-domain"),
        pytest.param(
            "@",
            "example.com",
            id="short-sub-domain",
        ),
    ],
)
def test_subdomain_not_managed(
    mock_db_for_test: Connection,
    capsys: CaptureFixture[str],
    expected_subdomain: str,
    expected_domain: str,
):
    """Expected behavior when the subdomain is not managed."""

    # Arrange the create_A_record mock.
    EXPECTED_DOMAIN_RECORD_ID = 1001
    EXPECTED_A_RECORD_NAME = expected_subdomain.removesuffix("." + expected_domain)
    EXPECTED_IP4_ADDRESS = "127.0.0.1"

    with mock_db_for_test:
        update_datetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        # Arrange: Insert EXPECTED_DOMAIN into the db
        # as a managed domain.
        mock_db_for_test.execute(
            "INSERT INTO domains(name, cataloged, last_managed) "
            " values(:name, :cataloged, :last_managed)",
            {
                "name": expected_domain,
                "cataloged": update_datetime,
                "last_managed": update_datetime,
            },
        )
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        # Arrange: Insert EXPECTED_SUBDOMAIN into the db
        # as an un-managed subdomain.
        mock_db_for_test.execute(
            "INSERT INTO subdomains("
            "   domain_record_id,"
            "   main_id,"
            "   name,"
            "   current_ip4,"
            "   cataloged,"
            "   last_checked,"
            "   last_updated,"
            "   managed"
            ") values("
            "   :domain_record_id,"
            "   :main_id,"
            "   :name,"
            "   :current_ip4,"
            "   :cataloged,"
            "   :last_checked,"
            "   :last_updated,"
            "   0"
            ")",
            {
                "domain_record_id": EXPECTED_DOMAIN_RECORD_ID,
                "main_id": 1,  # expected id from domains.id
                "name": EXPECTED_A_RECORD_NAME,
                "current_ip4": EXPECTED_IP4_ADDRESS,
                "cataloged": now,
                "last_checked": now,
                "last_updated": now,
            },
        )

    subdomains.un_manage_subdomain(subdomain=expected_subdomain, domain=expected_domain)

    # Validate the pre-existing subdomain was not updated in the database.
    row = mock_db_for_test.execute(
        "SELECT "
        "   domain_record_id,"
        "   main_id,"
        "   name,"
        "   current_ip4,"
        "   cataloged,"
        "   last_checked,"
        "   last_updated,"
        "   managed "
        "from subdomains "
        "WHERE "
        "name = :name",
        {"name": EXPECTED_A_RECORD_NAME},
    ).fetchone()

    # Validate: values have not changed.
    assert row["current_ip4"] == EXPECTED_IP4_ADDRESS
    assert row["domain_record_id"] == EXPECTED_DOMAIN_RECORD_ID
    assert row["cataloged"] == now
    assert row["last_checked"] == now
    assert row["last_updated"] == now
    assert row["main_id"] == 1  # expected id from domains.id
    assert row["managed"] == 0

    # Validate user output
    captured_errout = capsys.readouterr()
    assert "is not being managed by digital-ocean-dynamic-dns." in captured_errout.out


def test_non_simple_chars_in_domain_name():
    """Raise NonSimpleDomainNameError if non-simple characters are used."""
    with pytest.raises(subdomains.NonSimpleDomainNameError):
        subdomains.un_manage_subdomain(
            subdomain="\N{GREEK CAPITAL LETTER DELTA}-forge.example.com", domain="example.com"
        )
