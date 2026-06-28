# SPDX-FileCopyrightText: © 2023 Tyler Nivin
# SPDX-License-Identifier: MIT

"""Tests for the un_manage_subdomain function."""

import datetime as dt
from sqlite3 import Connection

import pytest

from digital_ocean_dynamic_dns import subdomains

pytestmark = pytest.mark.usefixtures("mocked_responses")


@pytest.mark.parametrize(
    ("expected_subdomain", "expected_domain"),
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
    capsys: pytest.CaptureFixture[str],
    expected_domain: str,
    expected_subdomain: str,
) -> None:
    """un_manage_subdomain raises TopDomainNotManagedError if the top domain is not managed.

    un_manage_subdomain() assumes the top domain is already being managed.
    """
    with pytest.raises(subdomains.TopDomainNotManagedError):
        subdomains.un_manage_subdomain(subdomain=expected_subdomain, domain=expected_domain)

    # Validate: We provide the user with some output, should we somehow reach this invalid state.
    capd_err_out = capsys.readouterr()
    assert f"Error: {expected_domain} is not a managed domain. " in capd_err_out.out


@pytest.mark.parametrize(
    ("expected_subdomain", "expected_domain"),
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
    capsys: pytest.CaptureFixture[str],
    expected_subdomain: str,
    expected_domain: str,
) -> None:
    """Verify expected side effects of un_manage_subdomain.

    Expected side effects:
        1. subdomain marked as un-managed in database.
        2. User-facing output is provided.
    """
    # Arrange the create_a_record mock.
    expected_domain_record_id = 1001
    expected_a_record_name = expected_subdomain.removesuffix("." + expected_domain)
    expected_ip4_address = "127.0.0.1"

    # Arrange: Insert expected_domain into the db
    # as a managed domain.
    with mock_db_for_test:
        update_datetime = dt.datetime.now(tz=dt.UTC).astimezone().strftime("%Y-%m-%d %H:%M")
        mock_db_for_test.execute(
            "INSERT INTO domains(name, cataloged, last_managed) "
            " values(:name, :cataloged, :last_managed)",
            {
                "name": expected_domain,
                "cataloged": update_datetime,
                "last_managed": update_datetime,
            },
        )
        # Arrange: Insert expected_subdomain into the db
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
                "domain_record_id": expected_domain_record_id,
                "main_id": 1,  # expected id from domains.id
                "name": expected_a_record_name,
                "current_ip4": expected_ip4_address,
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
        {"name": expected_a_record_name},
    ).fetchone()
    assert row is not None  # triggered when no match / no insert.

    # Validate: inserted values.
    assert row["current_ip4"] == expected_ip4_address
    assert row["domain_record_id"] == expected_domain_record_id
    now = dt.datetime.now(tz=dt.UTC).astimezone()
    assert dt.datetime.strptime(row["cataloged"], "%Y-%m-%d %H:%M").astimezone() <= now
    assert dt.datetime.strptime(row["last_checked"], "%Y-%m-%d %H:%M").astimezone() <= now
    assert dt.datetime.strptime(row["last_updated"], "%Y-%m-%d %H:%M").astimezone() <= now
    assert row["main_id"] == 1  # expected id from domains.id
    assert row["managed"] == 0

    # Validate user output
    captured_out = capsys.readouterr().out
    captured_out = " ".join(captured_out.split())
    assert (
        f"{expected_a_record_name} for domain {expected_domain}"
        " is no longer being managed by digital-ocean-dynamic-dns!" in captured_out
    )


@pytest.mark.parametrize(
    ("expected_subdomain", "expected_domain"),
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
    capsys: pytest.CaptureFixture[str],
    expected_subdomain: str,
    expected_domain: str,
) -> None:
    """Expected behavior when the subdomain is not managed."""
    # Arrange the create_a_record mock.
    expected_domain_record_id = 1001
    expected_a_record_name = expected_subdomain.removesuffix("." + expected_domain)
    expected_ip4_address = "127.0.0.1"

    with mock_db_for_test:
        update_datetime = dt.datetime.now(tz=dt.UTC).astimezone().strftime("%Y-%m-%d %H:%M")
        # Arrange: Insert expected_domain into the db
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
        now = dt.datetime.now(tz=dt.UTC).astimezone().strftime("%Y-%m-%d %H:%M")
        # Arrange: Insert expected_subdomain into the db
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
                "domain_record_id": expected_domain_record_id,
                "main_id": 1,  # expected id from domains.id
                "name": expected_a_record_name,
                "current_ip4": expected_ip4_address,
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
        {"name": expected_a_record_name},
    ).fetchone()

    # Validate: values have not changed.
    assert row["current_ip4"] == expected_ip4_address
    assert row["domain_record_id"] == expected_domain_record_id
    assert row["cataloged"] == now
    assert row["last_checked"] == now
    assert row["last_updated"] == now
    assert row["main_id"] == 1  # expected id from domains.id
    assert row["managed"] == 0

    # Validate user output
    captured_errout = capsys.readouterr()
    assert "is not being managed by digital-ocean-dynamic-dns." in captured_errout.out


def test_non_simple_chars_in_domain_name() -> None:
    """Raise NonSimpleDomainNameError if non-simple characters are used."""
    with pytest.raises(subdomains.NonSimpleDomainNameError):
        subdomains.un_manage_subdomain(
            subdomain="\N{GREEK CAPITAL LETTER DELTA}-forge.example.com", domain="example.com"
        )
