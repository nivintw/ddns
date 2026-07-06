<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

<!-- Shared content fragment, included via pymdownx.snippets (`--8<-- "install.md"`) from
     any docs page that needs install instructions, so they can't drift between copies
     (nivintw/repo-management#96). -->

`do_ddns` is published on PyPI as `digital-ocean-dynamic-dns` and requires Python >= 3.12.
Install it as an isolated CLI tool rather than into a project environment:

=== "pipx"

    ```bash
    pipx install digital-ocean-dynamic-dns
    ```

=== "uv"

    ```bash
    uv tool install digital-ocean-dynamic-dns
    ```

Either gives you a `do_ddns` command on your `PATH`.
