<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Troubleshooting

If `do_ddns` exited with an error, find the message it printed below. Each entry leads with
the fix.

!!! note
    Except for `show-info`, none of these errors are caught internally — the friendly message
    shown in each entry below (the exact text varies per error; not all of them start with
    `Error:`) is followed by a full Python traceback. That traceback is expected; the friendly
    message above it is the part that matters.

## `NoAPIKeyError`

**Looks like:**

```text
Error: Missing APIkey. Please set the DIGITALOCEAN_TOKEN environment variable!
```

**Fix:** export your DigitalOcean token before running any `do_ddns` command:

```bash
export DIGITALOCEAN_TOKEN=<your-do-token>
```

**Cause:** the `DIGITALOCEAN_TOKEN` environment variable isn't set in the shell (or scheduler
environment — cron and systemd don't inherit your interactive shell) that `do_ddns` is running in.
See [Configuration](configuration.md#api-token) for details.

## `NoIPResolverServerError`

**Looks like:**

```text
Please configure an IP resolver server.
```

**Fix:** configure an IP resolver before running `update-ips` or `manage`:

```bash
do_ddns ip-resolver-config --url https://api.ipify.org
```

**Cause:** any command that needs to resolve your public IP address (`update-ips`, `manage`) needs
an IP resolver configured first, and none has been set yet. See the
[`ip-resolver-config` command reference](commands/ip-resolver-config.md).

## `TopDomainNotManagedError`

This has two different causes depending on which command raised it — check which one you ran.

**From [`un-manage`](commands/un-manage.md) `--subdomain`:**

```text
Error: example.com is not a managed domain.
```

**Fix:** this is a normal usage error, not a bug — you ran `un-manage --subdomain` against a
domain `do_ddns` has never cataloged (a typo in the domain name, or a domain you never
[`manage`](commands/manage.md)d in the first place). Double-check the domain name, or run
`do_ddns manage <domain>` first if you meant to catalog it.

**From [`manage`](commands/manage.md) (bare, or `--subdomain`):**

```text
Error: example.com is not a managed domain. We do not expect users to ever be exposed to this
error. If you see this in the console while using digital-ocean-dynamic-dns please open an issue
on the repository.
```

**Fix:** this genuinely shouldn't happen — `manage` always manages the top-level domain itself
before touching a subdomain (see [manage](commands/manage.md)), so a normal `manage` invocation
can't hit this. If you see it, please
[file an issue](https://github.com/nivintw/ddns/issues) with the exact command you ran.

**Cause:** internal code tried to manage or un-manage a subdomain whose top-level domain isn't
marked as managed (`un-manage`) or managed at all (`manage`) in the local database.

## `NoManagedSubdomainsError`

**Looks like:**

```text
Error: There are no dynamic domains active. Start by adding a new domain with do_ddns manage.
E.g. do_ddns manage example.com --subdomain test.
```

**Fix:** manage at least one domain (or subdomain) before running `update-ips`:

```bash
do_ddns manage example.com --subdomain home
```

**Cause:** `update-ips` was run but zero subdomains are currently managed, so there's nothing to
update. See the [`manage` command reference](commands/manage.md).

## `IPv6NotSupportedError`

**Looks like:**

```text
IPv6 is not currently supported.
```

**Fix:** use `--ip-mode 4` (the default) instead:

```bash
do_ddns ip-resolver-config --url https://api.ipify.org --ip-mode 4
```

**Cause:** `ip-resolver-config --ip-mode 6` was used. IPv6 isn't supported yet — see the
[roadmap](roadmap.md) for the current state of IPv6 support.

## `NonSimpleDomainNameError`

**Looks like:**

```text
Error: Give the domain name in simple form e.g. test.domain.com
```

**Fix:** pass the plain ASCII form of the domain/subdomain name, e.g. `test.domain.com` rather
than a fully-qualified trailing-dot form, an internationalized domain name, or anything with
unexpected punctuation.

**Cause:** the domain or subdomain name given to `manage`/`un-manage` contains characters outside
ASCII letters, digits, `.`, `-`, and `@`.
