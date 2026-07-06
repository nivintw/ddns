<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Configuration

Reference for everything `do_ddns` reads or stores to do its job: the API token, the IP resolver,
and the files it keeps on disk.

## API token

`do_ddns` needs a DigitalOcean [Personal Access Token](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
with DNS read/write scope, provided via the `DIGITALOCEAN_TOKEN` environment variable:

```bash
export DIGITALOCEAN_TOKEN=<your-do-token>
```

This is the only configuration path today — there's no config-file support yet. `DIGITALOCEAN_TOKEN`
is the same environment variable name DigitalOcean's own [`pydo`](https://pydo.readthedocs.io/en/latest/)
library uses, by design, so tooling already configured for `pydo` works with `do_ddns` for free.
Config-file support is tracked as a possible future improvement — see the [roadmap](roadmap.md).

If the variable isn't set, every command that needs to talk to the DigitalOcean API fails
immediately. See [Troubleshooting](troubleshooting.md#noapikeyerror) for the exact error and fix.

## IP resolver

`do_ddns` learns your public IP by making a GET request to a URL you configure and reading the
plain-text response body. Unlike the API token, this isn't an environment variable — it's set
with a command and stored in the local SQLite database:

```bash
do_ddns ip-resolver-config --url https://api.ipify.org
```

See the [`ip-resolver-config` command reference](commands/ip-resolver-config.md) for the full set
of options.

Only IPv4 is functional today. Passing `--ip-mode 6` is a hard error
(`IPv6NotSupportedError`) — see [Troubleshooting](troubleshooting.md#ipv6notsupportederror) and the
[roadmap](roadmap.md) for the current state of IPv6 support.

## Local data & files

`do_ddns` computes where to keep its state using the [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/index.html)
convention: `$XDG_DATA_HOME` if it's set, otherwise `~/.local/share`, namespaced under
`tech.nivin.digital-ocean-dynamic-dns/`.

| File | Default location | Purpose |
| --- | --- | --- |
| `do_ddns.db` | `~/.local/share/tech.nivin.digital-ocean-dynamic-dns/do_ddns.db` | SQLite database holding all persisted state (IP resolver, managed domains/subdomains). |
| `do_ddns.log` | `~/.local/share/tech.nivin.digital-ocean-dynamic-dns/do_ddns.log` | Plain-text log file, INFO level, appended to via Python's standard `logging` module. |

If `XDG_DATA_HOME` is set, both files live under `$XDG_DATA_HOME/tech.nivin.digital-ocean-dynamic-dns/`
instead. Use `do_ddns logs` to print the log file's contents from the CLI.

## Database schema

The SQLite database (`do_ddns.db`) has three tables:

- **`ipservers`** — the configured IP resolver (URL and IP version). Written by
  `ip-resolver-config`.
- **`domains`** — a catalog of domains `do_ddns` knows about, each flagged managed or unmanaged.
  Written by `manage`/`un-manage`.
- **`subdomains`** — a catalog of subdomains (A records) `do_ddns` knows about, each flagged
  managed or unmanaged, along with the DigitalOcean A-record ID it corresponds to. Written by
  `manage`/`un-manage`.

This is a brief orientation for troubleshooting, not a full schema reference — the database is an
implementation detail and its exact columns may change between releases.

## Platform support

**Windows is not supported today.** `do_ddns` raises a hard error on startup on Windows, before it
does anything else. If you're on Windows, this tool won't run — there's no workaround short of
running it under WSL or a Linux/macOS environment. Linux and macOS are both supported via the XDG
convention described above.
