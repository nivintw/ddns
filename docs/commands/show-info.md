<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# show-info

Prints a summary of the current `do_ddns` configuration and installation: API key status, IP
resolver, log file location, domain/subdomain counts, and app version.

## Usage

```bash
do_ddns show-info
do_ddns show-info --show-api-key
do_ddns show-info --no-show-api-key  # explicit form of the default
do_ddns show-info domains
```

`--show-api-key` / `--no-show-api-key` is a
[`BooleanOptionalAction`](https://docs.python.org/3/library/argparse.html#argparse.BooleanOptionalAction);
the default is `--no-show-api-key`.

## What it does

| Invocation | Behavior |
| --- | --- |
| `show-info` | Prints a table: API key status (configured/missing, masked unless `--show-api-key`), configured IPv4 resolver, log file path, total domain count, total subdomain ("A" record) count, and app version. |
| `show-info --show-api-key` | Same table, but with the actual API key value shown instead of `Configured`. |
| `show-info domains` | Lists every domain registered on the DigitalOcean account, one per line, marking each one already cataloged locally with `[*]`. |

The `[*]` marker on `show-info domains` reflects whether the domain has a row in the local
database at all — cataloging alone is enough to earn the marker, whether or not the domain is
currently `managed`.

## When to reach for it

Reach for the bare form as a health check: confirm the API key is set, a resolver is
configured, and see how many domains/subdomains are tracked, without digging into per-domain
detail. Reach for `show-info domains` specifically when you need to see the full list of
domains available on the account — including ones `do_ddns` has never touched — before
deciding what to [`manage`](manage.md).

!!! note
    `show-info domains` marks a domain cataloged, not necessarily managed. A domain you
    previously `un-manage`d still shows `[*]` here, since un-managing never removes its
    database row.

## Related

- [logs](logs.md) — the log file path shown here is the same file `logs` prints.
- [manage](manage.md) — `manage <domain> --list` gives per-domain subdomain detail; `show-info`
  gives the account-wide summary.
- [Configuration](../configuration.md) — where the log file, API key, and database live on disk.
