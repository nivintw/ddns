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

## Appendix

This is an appendix of the various terms used in the library.

domain: A domain as described by Digital Ocean (see [Digital Ocean's DNS quickstart](https://docs.digitalocean.com/products/networking/dns/getting-started/quickstart/)).
This is specifically a "two part" domain such as "example.com" without any sub-domains specified.

subdomain: A subdomain as described by Digital Ocean (see [Digital Ocean's add-a-subdomain guide](https://docs.digitalocean.com/products/networking/dns/how-to/add-subdomain/)).
This can be any subdomain that Digital Ocean supports.
Subdomains must be associated with a registered and managed domain.

manage (domain context): Refers specifically to having digital-ocean-dynamic-dns catalog the corresponding domain.
Domains must be managed by digital-ocean-dynamic-dns in order to manage corresponding subdomains.

manage (subdomain context): Refers specifically to having digital-ocean-dynamic-dns handle updating the IP address associated with the corresponding subdomain.

un-manage (domain context): Mark the corresponding domain as un-managed in the digital-ocean-dynamic-dns local database/catalog.
This will have the effect of un-managing (but not de-registering nor remove) the corresponding subdomains.

un-manage (subdomain context): Mark the corresponding subdomain as un-managed in the digital-ocean-dynamic-dns local database/catalog.
This will result in the IP address no longer being managed by digital-ocean-dynamic-dns.
This does not remove the entry for the subdomain from the local digital-ocean-dynamic-dns database/catalog.
This will not de-register the associated subdomain.

remove (domain context): Removes the associated domain from the digital-ocean-dynamic-dns local database/catalog.
This has the additional effect of removing corresponding subdomains.
No de-register actions are taken as part of a remove action; changes are to the digital-ocean-dynamic-dns local database/catalog only.

remove (subdomain context): Removes the associated subdomain from the digital-ocean-dynamic-dns local database/catalog.
No de-register actions are taken as part of a remove action; changes are to the digital-ocean-dynamic-dns local database/catalog only.

catalog: Store an entry in the digital-ocean-dynamic-dns database for the corresponding domain or subdomain.
Domains and subdomains can be cataloged and not managed.

register (subdomain context): Make changes to you Digital Ocean account to add the corresponding subdomain record to the corresponding Domain registration.
This requires that the top domain (e.g. example.com for subdomain my.example.com) be both registered and managed.

deregister (subdomain context): Make changes to your Digital Ocean account to remove the corresponding subdomain records from the corresponding Domain registration.
This has the additional effect of removing the subdomain from the local digital-ocean-dynamic-dns database.

## Planned Updates

- [ ] Add support for multiple IP address resolvers.
  - examples: `https://ip-api.com`, `https://api.whatismyip.com/ip.php?key=<API_KEY>`, etc
- [ ] Finish updating the command line user interface.
  - Substantial changes have already been made, and further re-writes are planned.
  - [/] changes to using subparsers instead of overloaded command line flags.
  - [/] Revise language to be more clear about what is being managed and how.
  - [ ] substantial changes to argparse usage/implementation
- [ ] Update README.md to highlight where/how this tool is intended to be used.
- [ ] Update logging features/implementation.
- [ ] Register and upload package to PyPI.
- [ ] Add automated CI/CD process including package release to PyPI.
- [ ] Integrate python-semantic-release for version management.
- [ ] Add support for purging local database (without updating DO records).
  - Used to just get a "fresh install".
- [ ] Add support to read config from a toml file.
