import sqlite3
from pathlib import Path
from sqlite3 import Connection
from typing import Literal

import pytest

from ddns_digital_ocean import api_key_helpers, ddns
from ddns_digital_ocean.database import connect_database


@pytest.fixture()
def mock_db_for_test(temp_database_path: Path, mocker):
    """Mock api_key_helpers.conn to have a per-test connection / database.
    Ensures isolation of the database state between tests.

    In this module we have to mock out the conn objects everywhere they are created
      in order to ensure all modules/functions are using the same databases.

    """
    test_specific_conn = connect_database(temp_database_path)
    test_specific_conn.row_factory = sqlite3.Row
    mocker.patch.object(ddns, "conn", test_specific_conn)
    mocker.patch.object(api_key_helpers, "conn", test_specific_conn)

    return test_specific_conn


@pytest.fixture()
def preload_api_key(mock_db_for_test: Connection):
    """Load a sentinel API key.
    Almost all operations require an api key to be configured.
    This fixture provides a sentinel / not-real API key for us to use.
    """
    SENTINEL_API_KEY = "sentinel-api-key"  # pragma: allowlist secret
    api_key_helpers.set_api_key(SENTINEL_API_KEY)
    return SENTINEL_API_KEY


@pytest.mark.usefixtures("mock_db_for_test")
class TestAddDomain:
    def test_add_domain_empty_db(
        self,
        requests_mock,
        preload_api_key: Literal["sentinel-api-key"],
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
    ):
        """Add a domain to an empty database."""

        EXPECTED_NEW_DOMAIN = "sentinel.new.test.domain.local"
        # See: https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_get
        MOCKED_RESP_JSON = {
            "domain": {
                "name": "example.com",
                "ttl": 1800,
                "zone_file": (
                    "$ORIGIN example.com.\n"
                    "$TTL 1800\n"
                    "example.com. IN SOA ns1.digitalocean.com. "
                    "hostmaster.example.com. 1415982611 10800 3600 604800 1800\n"
                    "example.com. 1800 IN NS ns1.digitalocean.com.\n"
                    "example.com. 1800 IN NS ns2.digitalocean.com.\n"
                    "example.com. 1800 IN NS ns3.digitalocean.com.\n"
                    "example.com. 1800 IN A 1.2.3.4\n"
                ),
            }
        }
        # Arrange: Configure HTTP requests to mock out.
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        requests_mock.get(
            "https://api.digitalocean.com/v2/domains/" + EXPECTED_NEW_DOMAIN,
            request_headers=headers,
            json=MOCKED_RESP_JSON,
        )

        ddns.add_domain(EXPECTED_NEW_DOMAIN)

        # Validate: Ensure domain was added to the database.
        with mock_db_for_test:
            cursor = mock_db_for_test.execute(
                "SELECT * FROM domains where name = ?", (EXPECTED_NEW_DOMAIN,)
            )
            row = cursor.fetchone()
            assert row is not None
            assert row["name"] == EXPECTED_NEW_DOMAIN
            assert row["id"] == 1

        # Validate: Ensure user was informed.
        captured_output = capsys.readouterr()
        assert f"The domain {EXPECTED_NEW_DOMAIN} has been added to the DB" in captured_output.out

    @pytest.mark.usefixtures("preload_api_key", "requests_mock")
    def test_add_domain_already_in_db(
        self,
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
    ):
        """If user tries to add a DB already in the database we alert them and change nothing.

        Note: I don't configure any mocked requests because,
          the way this test and the function under test are written,
          no http(s) requests should be made.

        Validates:
            1. No requests are made
                - If there were a request, it would mean we haven't early-exited
                    after checking the local db.
            2. Output contains 'already in database!' message.
                - If this message is not in stdout,
                    then the user doesn't get feedback on what happened.
        """
        EXPECTED_EXISTING_DOMAIN = "sentinel.existing.test.domain.local"

        # Arrange: inject the domain directly into the table before
        # calling the function under test.
        with mock_db_for_test:
            mock_db_for_test.execute(
                "INSERT INTO domains values(?,?)",
                (
                    None,
                    EXPECTED_EXISTING_DOMAIN,
                ),
            )

        ddns.add_domain(EXPECTED_EXISTING_DOMAIN)

        captured_output = capsys.readouterr()
        assert (
            f"Domain name ({EXPECTED_EXISTING_DOMAIN}) already in database!" in captured_output.out
        )

    @pytest.mark.parametrize(
        "status_code, json_response, expected_stdout",
        [
            pytest.param(
                401,
                {"id": "unauthorized", "message": "Unable to authenticate you."},
                "The api key that is configured resulted in an unauthorized response.",
                id="unauthorized",
            ),
            pytest.param(
                404,
                {"id": "not_found", "message": "The resource you requested could not be found."},
                "The domain does not exist in your DigitalOcean account.",
                id="not_found",
            ),
            pytest.param(
                429,
                {"id": "too_many_requests", "message": "API Rate limit exceeded."},
                "API Rate limit exceeded. Please try again later.",
                id="too_many_requests",
            ),
            pytest.param(
                500,
                {"id": "server_error", "message": "Unexpected server-side error"},
                "Unexpected Internal Server Error Response from DigitalOcean. ",
                id="server_error",
            ),
            pytest.param(
                10_000,
                {"id": "example_error", "message": "some error message"},
                "Completely unexpected error response from Digital Ocean.",
                id="do_default_error",
            ),
        ],
    )
    @pytest.mark.usefixtures("mock_db_for_test")
    def test_invalid_upstream_responses(
        self,
        status_code,
        json_response,
        expected_stdout,
        requests_mock,
        preload_api_key: Literal["sentinel-api-key"],
        mock_db_for_test: Connection,
        capsys: pytest.CaptureFixture[str],
    ):
        """We handle all documented upstream error states.

        See: https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_get
        """

        EXPECTED_NEW_DOMAIN = "sentinel.new.test.domain.local"

        # Arrange: Configure HTTP requests to mock out.
        headers = {
            "Authorization": "Bearer " + preload_api_key,
            "Content-Type": "application/json",
        }
        requests_mock.get(
            "https://api.digitalocean.com/v2/domains/" + EXPECTED_NEW_DOMAIN,
            request_headers=headers,
            json=json_response,
            status_code=status_code,
        )

        ddns.add_domain(EXPECTED_NEW_DOMAIN)

        # Validate: user was informed of failure situation.
        captured_output = capsys.readouterr()
        assert expected_stdout in captured_output.out

        # Validate: nothing was added to the database.
        row = mock_db_for_test.execute(
            "SELECT * FROM domains where name = ?", (EXPECTED_NEW_DOMAIN,)
        ).fetchone()
        assert row is None
