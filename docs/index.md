<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Digital Ocean Dynamic DNS

`do_ddns` keeps DigitalOcean DNS A-records pointed at a network with a dynamic IP address. It
polls your public IP and, when it changes, updates the A-records you've told it to manage — so a
domain hosted on DigitalOcean keeps resolving to your home (or any residential) connection without
you touching anything by hand.

This is for self-hosters: if your ISP doesn't give you a static IP but you still want a stable
domain name pointing at a server, NAS, or gateway on your network, this tool closes that gap.

## At a glance

```bash
export DIGITALOCEAN_TOKEN=<your-do-token>
do_ddns ip-resolver-config --url https://api.ipify.org
do_ddns manage example.com --subdomain home
do_ddns update-ips
```

That's a one-time setup followed by the command you'd run on a schedule (cron, a systemd timer,
...) to keep records current.

## Where to next

- **[Getting Started](getting-started.md)** — install, configure, and onboard your first domain,
  including scheduling `update-ips` to run automatically.
- **[Commands](commands/index.md)** — full reference for every `do_ddns` subcommand and flag.
- **[Concepts](concepts.md)** — the domain/subdomain/manage/catalog vocabulary this tool uses.
