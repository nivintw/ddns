<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# digital-ocean-dynamic-dns

[![pre-commit enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![CI status badge](https://img.shields.io/github/actions/workflow/status/nivintw/ddns/main.yml?branch=main&label=CI&logo=github)](https://github.com/nivintw/ddns/actions/workflows/main.yml)

Dynamic DNS python tool for Digital Ocean

This project offers a way to manage dynamic DNS, with specific support for [DigitalOcean](https://www.digitalocean.com/) authoritative DNS servers.

Example:

1. I own the domain `nivin.tech`
1. DigitalOcean is my authoritative name server provider for the `nivin.tech` domain.
1. I use this package (installed as a command line utility and deployed on a device on my home network) to update the DNS records for `nivin.tech` to point at my home gateway, which is assigned a dynamic IP address by my internet service provider (ISP).

## Documentation

Full docs — installation, first-run setup, the complete command reference, and
troubleshooting — live under [`docs/`](docs/index.md). These are repo-relative links: they
render correctly on GitHub, but not from PyPI's rendered long description (this README) —
see [nivintw/ddns#38](https://github.com/nivintw/ddns/issues/38) to switch to absolute links
once this content actually exists on `main` (converting now would 404 until this very PR
merges):

- [Getting Started](docs/getting-started.md) — install, configure, onboard your first domain
- [Commands](docs/commands/index.md) — every `do_ddns` subcommand and flag
- [Concepts](docs/concepts.md) — the domain/subdomain/manage/catalog vocabulary
- [Configuration](docs/configuration.md) — env vars, file locations, platform limits
- [Troubleshooting](docs/troubleshooting.md) — common errors and fixes
- [Roadmap](docs/roadmap.md) — known limitations and planned work

This project carries the shared quality baseline: prek hooks (git hygiene, gitleaks,
typos, rumdl, SPDX/REUSE headers, ruff, ty) that run
identically locally and in CI. Conventional Commits are enforced at commit-msg time
(`.cz.toml`); releases on `main` are managed by release-please (a Release PR →
`vX.Y.Z` tag + GitHub Release on merge).

## Installation

See [Getting Started](docs/getting-started.md#1-install) for install instructions (pipx or uv).

## License

[MIT](LICENSE) — and [REUSE](https://reuse.software)-compliant.
