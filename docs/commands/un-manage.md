<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# un-manage

Stops `do_ddns` from tracking a domain or subdomain, so future
[`update-ips`](update-ips.md) runs no longer touch its A-record.

## Usage

```bash
do_ddns un-manage example.com
do_ddns un-manage example.com --subdomain home
do_ddns un-manage example.com --subdomain home.example.com
do_ddns un-manage example.com --list
```

`--subdomain` and `--list` are mutually exclusive — this mirrors [`manage`](manage.md)'s shape
exactly.

## What it does

| Invocation | Behavior |
| --- | --- |
| `un-manage <domain>` | Un-manages `<domain>` **and** cascades to every subdomain currently managed under it. |
| `un-manage <domain> --subdomain <name>` | Un-manages only `<name>`; the parent domain and any other subdomains are untouched. |
| `un-manage <domain> --list` | Prints managed and unmanaged A-records for `<domain>`. Read-only — makes no changes. |

As with `manage`, a subdomain name can be given bare (`home`) or fully-qualified
(`home.example.com`) — the domain suffix is stripped automatically.

## When to reach for it

Use the bare form when you're walking away from a domain entirely — it un-manages the domain
and every subdomain under it in one call. Use `--subdomain` to drop a single subdomain while
leaving the rest of the domain's records under management (for example, decommissioning one
host but keeping others current).

!!! warning
    `un-manage` does **not** delete the DNS A-record from DigitalOcean, and does not remove the
    row from the local database. It only flips a `managed` flag off, so `update-ips` skips it
    going forward. The record stays live upstream at whatever IP it last had. See
    [Concepts](../concepts.md) for how manage/un-manage relate to cataloging and actual removal.

## Related

- [manage](manage.md) — the inverse: start tracking a domain or subdomain again.
- [update-ips](update-ips.md) — un-managed subdomains are the ones this command will now skip.
- [Concepts](../concepts.md) — the manage vs. un-manage vs. catalog vs. remove distinction,
  spelled out in full.
