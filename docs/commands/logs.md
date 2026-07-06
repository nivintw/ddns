<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# logs

Dumps the current contents of `do_ddns`'s log file to the console.

## Usage

```bash
do_ddns logs
```

Takes no arguments.

## What it does

1. Opens the application's log file (INFO-level Python logging, populated primarily by
   [`update-ips`](update-ips.md) runs).
2. Reads its entire current contents.
3. Prints it as-is — no filtering, tailing, or formatting.

## When to reach for it

Reach for this after a scheduled `update-ips` run to confirm it actually ran and whether it
found anything to update, or when diagnosing why records aren't updating as expected. It's a
full dump rather than a tail, so on a long-lived install expect to pipe the output through your
own pager or filter.

## Related

- [show-info](show-info.md) — shows the log file's on-disk location.
- [Configuration](../configuration.md) — documents the log file's location and format in full.
