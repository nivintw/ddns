<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Roadmap & known limitations

What this tool doesn't do yet, verified against the current codebase — not a wishlist, a
status page.

## Known limitations today

- **Windows isn't supported.** The tool raises an error on startup on anything other than
  Linux or macOS.
- **Only IPv4 is supported.** [`ip-resolver-config --ip-mode 6`](commands/ip-resolver-config.md)
  raises an error rather than working.
- **Only one IP resolver at a time.** You can't configure a fallback/secondary resolver
  service — see [Configuration](configuration.md).
- **No config file.** All configuration is the `DIGITALOCEAN_TOKEN` environment variable
  plus CLI flags and locally-stored settings — see [Configuration](configuration.md).
- **No `remove`/`register`/`deregister` commands.** [`manage`](commands/manage.md) and
  [`un-manage`](commands/un-manage.md) are the only local state changes available today —
  see [Concepts](concepts.md#register-deregister-and-remove-not-yet-implemented-as-commands)
  for what's missing and why.

## Planned work

- Support multiple IP resolvers (e.g. a fallback service if the primary is unreachable).
- Continue revising the CLI: the move to argparse subparsers and clearer manage/un-manage
  language are done; further argparse-usage cleanup is still planned.
- Update the logging implementation (currently a single INFO-level log file with no
  rotation or structured output).
- Add support for purging the local database — a clean "fresh install" without touching
  DigitalOcean.
- Add support for reading configuration from a TOML file, instead of environment variables
  and CLI flags alone.

## Already done (superseded items from the original roadmap)

A few earlier goals are already live, in some cases via a different tool than originally
planned:

- **Published to PyPI** — released as
  [`digital-ocean-dynamic-dns`](https://pypi.org/project/digital-ocean-dynamic-dns/).
- **Automated releases** — release-please cuts tagged GitHub Releases from Conventional
  Commits on every merge to `main`. The originally-planned tool for this was
  python-semantic-release; release-please was used instead.
- **Automated PyPI publish pipeline (wired, not yet fully live)** — a publish workflow
  exists that builds once and pushes to TestPyPI then PyPI via OIDC Trusted Publishing, but
  the one-time PyPI/TestPyPI Trusted Publisher registration is still outstanding, so the
  last release didn't actually publish through it. Tracked separately, not a docs concern.

Have an idea, or hit one of the limitations above harder than expected? Open an issue on
[nivintw/ddns](https://github.com/nivintw/ddns/issues).
