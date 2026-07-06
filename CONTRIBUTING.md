<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# Contributing to Digital Ocean Dynamic DNS

Thanks for contributing!

## Workflow

1. Branch off `main` and land changes via a PR (enable branch protection to enforce it).
2. Run `uv sync` to set up the dev environment, then install the hooks: `uvx prek@0.4.8 install`.
3. Make your change. The pre-commit hooks run the full quality gate — the same checks run in CI.
4. Commit with [Conventional Commits](https://www.conventionalcommits.org), enforced by
   commitizen at commit-msg time. release-please cuts releases from these commits (a
   Release PR → `vX.Y.Z` tag + GitHub Release on merge), so keep the type prefix accurate.
5. Open a PR and make sure CI is green before requesting review.

## Running the quality gate

```bash
uvx prek@0.4.8 run --all-files
```

## Releasing

Published to **[PyPI](https://pypi.org/project/digital-ocean-dynamic-dns/)** on each GitHub Release
(`.github/workflows/publish.yml`), dress-rehearsed through **TestPyPI** first — build once,
publish to TestPyPI, install and import the built wheel, then (gated on that) publish to
PyPI. Auth is OIDC **Trusted Publishing** (no long-lived secret), bound to two GitHub
**deployment environments** — `testpypi` and `pypi` — each restricted to `v*` tag
deployments.

One-time setup before the first release:

1. Create the `testpypi` and `pypi` environments (repo Settings → Environments), each with
   a deployment branch/tag policy restricted to `v*` tags.
2. Add a pending Trusted Publisher on [test.pypi.org](https://test.pypi.org/manage/account/publishing/)
   and [pypi.org](https://pypi.org/manage/account/publishing/), each pointing at owner
   `nivintw`, repo `ddns`, workflow `publish.yml`, and the matching
   environment (`testpypi` / `pypi`).

Until both publishers exist, `uv publish` fails loudly rather than silently skipping.
