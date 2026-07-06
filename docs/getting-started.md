<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Getting Started

This walks through installing `do_ddns`, configuring it, and getting your first domain under
management.

## 1. Install

--8<-- "install.md"

## 2. Configure your API token

`do_ddns` needs a DigitalOcean [Personal Access Token](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
with DNS read/write scope. Export it as an environment variable:

```bash
export DIGITALOCEAN_TOKEN=<your-do-token>
```

See [Configuration: API token](configuration.md#api-token) for why this specific variable
name was chosen and what happens if it's unset.

## 3. Set up an IP resolver (one-time)

Point `do_ddns` at a service that reports your public IP:

```bash
do_ddns ip-resolver-config --url https://api.ipify.org
```

See the [`ip-resolver-config` command reference](commands/ip-resolver-config.md) for how the
resolver works and its full set of options. Only IPv4 is supported today.

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

On macOS, either adapt the cron example above (macOS ships `cron`) or use `launchd` — see
[Apple's Creating Launch Daemons and Agents guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
for details on writing a launch agent.

## 6. Inspect state

`do_ddns show-info` prints your current configuration (API key status, IP resolver, version), and
`do_ddns logs` prints the tool's logs. See the [Commands reference](commands/index.md) for the
full set of subcommands and flags.
