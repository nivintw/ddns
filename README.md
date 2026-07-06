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
troubleshooting — live under [`docs/`](docs/index.md):

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

Recommended installation path is to install this repository using [pipx](https://github.com/pypa/pipx). `pipx` provides the ability to install command line tools like this one into isolated environments, keeping your system-level packages clean and removing the possibility of dependency conflicts across tools.

Another alternative option to `pipx` is the (relatively) new tool [uv](https://github.com/astral-sh/uv). See [this blog post](https://astral.sh/blog/uv-unified-python-packaging) for more information and information on the recent features added to `uv`. If going the uv route, you want `uv tool install`.

## Publishing to PyPI

Published to **[PyPI](https://pypi.org/project/digital-ocean-dynamic-dns/)** on each GitHub Release
(`.github/workflows/publish.yml`), dress-rehearsed through **TestPyPI** first — build once,
publish to TestPyPI, install and import the built wheel, then (gated on that) publish to
PyPI. Auth is OIDC **Trusted Publishing** (no long-lived secret), bound to two GitHub
**deployment environments** — `testpypi` and `pypi` — each restricted to `v*` tag
deployments.

One-time setup before the first release:

1. Create the `testpypi` and `pypi` environments (repo Settings → Environments), each with
   a deployment branch/tag policy restricted to `v*` tags.
2. Add a pending Trusted Publisher on [test.pypi.org](https://test.pypi.org/manage/account/publishing/)
   and [pypi.org](https://pypi.org/manage/account/publishing/), each pointing at owner
   `nivintw`, repo `ddns`, workflow `publish.yml`, and the matching
   environment (`testpypi` / `pypi`).

Until both publishers exist, `uv publish` fails loudly rather than silently skipping.

## License

[MIT](LICENSE) — and [REUSE](https://reuse.software)-compliant.
