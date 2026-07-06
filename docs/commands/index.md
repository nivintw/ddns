<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Commands

`do_ddns` is a single entry point with six subcommands. Each one is documented in full on its
own page, linked below.

| Command | Description |
| --- | --- |
| [`update-ips`](update-ips.md) | Check (and, if needed, update) the public IP address recorded for every managed subdomain. |
| [`manage`](manage.md) | Start tracking a domain, or a single subdomain, so `update-ips` will keep its A-record current. |
| [`un-manage`](un-manage.md) | Stop tracking a domain or subdomain, without touching its DNS A-record or local database entry. |
| [`ip-resolver-config`](ip-resolver-config.md) | View or set the upstream service used to resolve your public IP address. |
| [`show-info`](show-info.md) | Display current configuration, counts, version, and (via a sub-subcommand) all upstream domains. |
| [`logs`](logs.md) | Print the contents of the application's log file. |
