<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Concepts

`digital-ocean-dynamic-dns` tracks its own state locally (in a SQLite database — see
[Configuration](configuration.md)) alongside whatever's actually registered with
DigitalOcean. The vocabulary below distinguishes what's tracked *locally* from what's
changed *upstream* — mixing these up is the most common source of confusion.

## Domain and subdomain

**Domain** — a two-part domain (`example.com`) as
[DigitalOcean defines it](https://docs.digitalocean.com/products/networking/dns/getting-started/quickstart/).

**Subdomain** — any subdomain of a managed domain
([DigitalOcean's definition](https://docs.digitalocean.com/products/networking/dns/how-to/add-subdomain/)),
e.g. `home.example.com`. A subdomain can only be tracked once its top-level domain is
managed.

## Catalog, manage, and un-manage

These three actions only touch the **local database** — none of them change anything on
DigitalOcean by themselves.

| Term | Domain context | Subdomain context |
| --- | --- | --- |
| **catalog** | Store a domain entry in the local database, without tracking IP updates for it. | Store a subdomain entry in the local database, without tracking IP updates for it. |
| **manage** | Catalog the domain *and* mark it eligible for subdomain tracking — a domain must be managed before any of its subdomains can be. | Catalog the subdomain *and* have `update-ips` keep its DigitalOcean A-record pointed at your current public IP. |
| **un-manage** | Mark the domain (and cascade to all its currently-managed subdomains) as no longer tracked. Does **not** delete the database entry or touch DigitalOcean. | Stop `update-ips` from touching this subdomain's A-record. Does **not** delete the database entry or touch DigitalOcean. |

In practice: `do_ddns manage example.com` catalogs and manages the domain in one step (see
[`manage`](commands/manage.md)) — you won't usually catalog something without also managing
it, but the distinction matters for [`show-info domains`](commands/show-info.md), which
marks *cataloged* domains regardless of whether they're actively managed.

## Register, deregister, and remove — not yet implemented as commands

Three more terms exist in this project's vocabulary but don't have a dedicated CLI command
today:

- **register** (subdomain context) — creating or claiming the actual DigitalOcean A-record
  for a subdomain. This happens as a *side effect* of [`manage`](commands/manage.md) (it
  creates the record if it doesn't exist, or claims an existing one) — there's no standalone
  `register` command.
- **deregister** (subdomain context) — removing a subdomain's A-record from DigitalOcean.
  No command does this yet; [`un-manage`](commands/un-manage.md) only stops local tracking,
  it never deletes anything on DigitalOcean.
- **remove** (domain/subdomain context) — deleting the local database entry entirely (as
  opposed to un-managing, which keeps the entry but marks it untracked). No command does
  this yet either.

If you need to delete a subdomain's A-record or database entry today, do it directly in the
DigitalOcean control panel / API — this tool won't touch it once un-managed. See the
[Roadmap](roadmap.md) for planned work in this area.
