<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# update-ips

Resolves your current public IP address and reconciles it against every subdomain
`do_ddns` is managing, updating only the DigitalOcean A-records that have drifted. This is
the command meant to run unattended, on a schedule.

## Usage

```bash
do_ddns update-ips
do_ddns update-ips --force
do_ddns update-ips --no-force  # explicit form of the default
```

`-f` is a short form of `--force`. Both flags are a
[`BooleanOptionalAction`](https://docs.python.org/3/library/argparse.html#argparse.BooleanOptionalAction),
so `--force` / `--no-force` are both accepted; the default is `--no-force`.

## What it does

1. Reads every subdomain currently marked `managed` in the local database. If there are none,
   it aborts before making any network calls (see the note below).
2. Resolves the host's current public IP address via the configured IPv4 resolver.
3. For each managed subdomain, fetches its A-record from the DigitalOcean API and compares the
   recorded IP against the current one.
4. If the IPs differ, or `--force` was given, it pushes an update to that A-record and updates
   the subdomain's `current_ip4` / `last_updated` / `last_checked` timestamps in the local
   database. If the IPs already match and `--force` was not given, it only updates
   `last_checked`.
5. Prints a one-line summary: either `No updates necessary` or `Updates done.` depending on
   whether any A-record actually changed.

## When to reach for it

This is the one command meant to run on a recurring schedule (cron, a systemd timer, ...) —
everything else here is one-time or occasional setup. Use `--force` only when you need to
push the current IP even though `do_ddns` believes the record is already current (for example,
after manually editing a record in the DigitalOcean dashboard).

!!! note
    `update-ips` raises an error if zero subdomains are currently managed — it will not
    silently no-op. Run [`manage`](manage.md) first to bring at least one subdomain under
    management.

## Related

- [manage](manage.md) — run this first if no subdomains are managed yet; `update-ips` refuses
  to run with nothing to check.
- [ip-resolver-config](ip-resolver-config.md) — `update-ips` also depends on a configured IP
  resolver; configure one before scheduling updates.
- [Getting Started: keep it updated](../getting-started.md#5-keep-it-updated) — the cron/systemd
  recipe for running this command automatically.
