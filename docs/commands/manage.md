<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# manage

Brings a domain, or a single subdomain of it, under `do_ddns` management so that
[`update-ips`](update-ips.md) will keep its A-record pointed at your current public IP.

## Usage

```bash
do_ddns manage example.com
do_ddns manage example.com --subdomain home
do_ddns manage example.com --subdomain home.example.com
do_ddns manage example.com --list
```

`--subdomain` and `--list` are mutually exclusive.

## What it does

| Invocation | Behavior |
| --- | --- |
| `manage <domain>` | Imports and manages **every** existing A-record already registered upstream for `<domain>`. |
| `manage <domain> --subdomain <name>` | Manages just `<name>`: claims the existing A-record if one exists upstream, or creates a new one if it doesn't. |
| `manage <domain> --list` | Prints managed and unmanaged A-records for `<domain>`. Read-only — makes no changes. |

In every mode, `manage` first ensures `<domain>` itself is registered as a managed top-level
domain (verifying it's actually registered on your DigitalOcean account before inserting it,
or doing nothing if it's already managed). Only after that does it act on `--subdomain` /
`--list` / the bare-domain import.

A subdomain name can be given bare (`home`) or fully-qualified (`home.example.com`) — `do_ddns`
strips the `.example.com` suffix automatically either way, so both forms are equivalent.

## When to reach for it

Use the bare form (`manage example.com`) when you already have A-records for a domain and want
`do_ddns` to take over updating all of them. Use `--subdomain` when you're onboarding one new
subdomain at a time, or when a domain has other A-records you don't want `do_ddns` touching.
Use `--list` any time you just want to check current state without side effects — it's the
per-domain counterpart to [`show-info`](show-info.md)'s account-wide summary.

!!! note
    The top-level domain is *always* attempted first, regardless of mode. Running
    `do_ddns manage example.com --subdomain home` manages **both** `example.com` and
    `home.example.com` in one call — you never need a separate step to manage the parent
    domain first.

## Related

- [update-ips](update-ips.md) — run this after `manage` to push the first update immediately,
  and on a schedule afterward.
- [un-manage](un-manage.md) — the inverse: stop tracking a domain or subdomain.
- [ip-resolver-config](ip-resolver-config.md) — configure an IP resolver first; `manage` needs
  one to create or claim an A-record.
- [Concepts](../concepts.md) — the domain/subdomain/manage/catalog vocabulary used throughout.
