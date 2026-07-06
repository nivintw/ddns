<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Getting Started

This walks through installing `do_ddns`, configuring it, and getting your first domain under
management.

## 1. Install

`do_ddns` is published on PyPI as `digital-ocean-dynamic-dns` and requires Python >= 3.12. Install
it as an isolated CLI tool rather than into a project environment:

=== "pipx"

    ```bash
    pipx install digital-ocean-dynamic-dns
    ```

=== "uv"

    ```bash
    uv tool install digital-ocean-dynamic-dns
    ```

Either gives you a `do_ddns` command on your `PATH`.

## 2. Configure your API token

`do_ddns` needs a DigitalOcean [Personal Access Token](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
with DNS read/write scope. Export it as an environment variable:

```bash
export DIGITALOCEAN_TOKEN=<your-do-token>
```

`DIGITALOCEAN_TOKEN` is the same environment variable name DigitalOcean's own [`pydo`](https://pydo.readthedocs.io/en/latest/)
library uses, by design — if you already have DigitalOcean tooling configured this way, `do_ddns`
picks it up for free.

## 3. Set up an IP resolver (one-time)

`do_ddns` figures out your current public IP by making a GET request to a URL you configure and
reading the plain-text response body. Point it at any service that returns your IP as plain text:

```bash
do_ddns ip-resolver-config --url https://api.ipify.org
```

Any URL that responds to a GET with your IP address as plain text works. Only IPv4 is supported
today.

## 4. Onboard a domain

Tell `do_ddns` which domain (and optionally which subdomain) to manage:

```bash
# Import and manage every existing A record on the domain
do_ddns manage example.com

# Or manage just one subdomain
do_ddns manage example.com --subdomain home
```

See the [`manage` command reference](commands/manage.md) for the full set of options, including
listing and un-managing records.

## 5. Keep it updated

Running the update once:

```bash
do_ddns update-ips
```

checks your current public IP and pushes any changes to the A-records you're managing. In
practice you want this running on a schedule so your DNS stays current without manual
intervention.

### Scheduling `update-ips`

=== "cron"

    Add a crontab entry to run every 15 minutes:

    ```cron
    */15 * * * * do_ddns update-ips
    ```

    Make sure `DIGITALOCEAN_TOKEN` is available to the cron environment (e.g. by setting it in the
    crontab itself or sourcing it from a file), since cron jobs don't inherit your interactive
    shell's environment.

=== "systemd timer"

    Create a service unit, `~/.config/systemd/user/do-ddns-update.service`:

    ```ini
    [Unit]
    Description=Update DigitalOcean dynamic DNS records

    [Service]
    Type=oneshot
    Environment=DIGITALOCEAN_TOKEN=<your-do-token>
    ExecStart=%h/.local/bin/do_ddns update-ips
    ```

    And a matching timer, `~/.config/systemd/user/do-ddns-update.timer`:

    ```ini
    [Unit]
    Description=Run do-ddns-update every 15 minutes

    [Timer]
    OnBootSec=5min
    OnUnitActiveSec=15min

    [Install]
    WantedBy=timers.target
    ```

    Enable and start the timer:

    ```bash
    systemctl --user enable --now do-ddns-update.timer
    ```

On macOS, either adapt the cron example above (macOS ships `cron`) or use `launchd` — see Apple's
[`launchd.plist` documentation](https://ss64.com/mac/launchd.html) for details on writing a
launch agent.

## 6. Inspect state

`do_ddns show-info` prints your current configuration (API key status, IP resolver, version), and
`do_ddns logs` prints the tool's logs. See the [Commands reference](commands/index.md) for the
full set of subcommands and flags.
