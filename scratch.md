# Scratch

- NOTE: Digital Ocean API's pagination urls drop filters (and thus can't be used to paginate)
- NOTE: Digital Ocean API's meta.total value in the response is ALL POSSIBLE records, NOT the number of records in the response.
  - I.e., it does not account for pagination (but does seem to account for filters e.g. "type"="A" for domain records.)
    TODO: Update my code to account for these discrepancies i've found.

do_ddns

- manage
  - `example.com --subdomain @`
  - `example.com --subdomain support.example.com`
    - Automatic domain management via subdomain driven commands.
    - Keeps the focus on the management of A records.
    - let's you manage a sub-selection of all A records / subdomains for the given domain.
    - Will create or update the A record for the specified subdomain.
  - `example.com`
    - start managing IP addresses for all current A records associated with `example.com`.
    - Will identify existing A records and begin managing those.
  - `example.com --list`
    - Show all A records for example.com.
    - Will show both managed and un-managed subdomains.
- un-manage

  - `example.com --subdomain support`
  - `example.com --subdomain support.example.com`
    - stop managing A records with the name `support` for the domain example.com.
  - `example.com`
    - stop managing all A records for example.com.
  - Leaves the current configuration in the database, marked un-managed.

- update_records (do automatic update for managed records)

  - no args
    - Updates IP addresses for A records on configured domains/subdomains.

- show-info
  - `do_ddns show-info`
  - `do_ddns show-info domains`
