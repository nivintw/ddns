<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# ip-resolver-config

Views or sets the upstream service `do_ddns` calls to learn your current public IP address.
This is one-time setup that has to happen before [`manage`](manage.md) or
[`update-ips`](update-ips.md) can do anything useful.

## Usage

```bash
do_ddns ip-resolver-config
do_ddns ip-resolver-config --url https://api.ipify.org
do_ddns ip-resolver-config --url https://api.ipify.org --ip-mode 4
```

## What it does

| Invocation | Behavior |
| --- | --- |
| `ip-resolver-config` (no args) | Prints the currently configured resolver URL, or `None Configured` if none is set. Makes no changes. |
| `ip-resolver-config --url <url>` | Sets (or overwrites) the resolver URL, then prints the resulting configuration. |

The resolver is expected to respond to a `GET` request with the caller's IP address as plain
text in the response body (for example, `https://api.ipify.org`). `--ip-mode` defaults to `4`
and only one resolver is stored at a time — setting a new URL overwrites the previous one.

## When to reach for it

Run this once, right after installing `do_ddns` and before your first `manage` call — nothing
that resolves an IP address will work without it. Re-run it later only if you need to switch
resolver services (for example, if your current one goes down).

!!! warning
    `--ip-mode 6` raises a hard error today — `IPv6NotSupportedError`. IPv4 is the only
    supported mode; don't pass `--ip-mode 6` expecting it to work.

## Related

- [manage](manage.md) — the next step once a resolver is configured.
- [update-ips](update-ips.md) — also depends on a configured resolver to know the current IP.
- [Getting Started: set up an IP resolver](../getting-started.md#3-set-up-an-ip-resolver-one-time) —
  a walkthrough of this one-time setup step.
