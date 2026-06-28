<!--
SPDX-FileCopyrightText: © 2023 Tyler Nivin
SPDX-License-Identifier: MIT
-->

# ship: adopt copier-everything template in ddns

Branch: worktree-chore+adopt-copier-template (base origin/main @ 55f1ef8 / 1.3.7)
Tracking issue: nivintw/ddns#16 (clone of repo-management#12). PR will `Closes #16`.
Template: gh:nivintw/copier-everything @ v1.1.0.

## Confirmed decisions (user sign-off)

1. Lint/type: **fix everything** — clear all ~700 ruff ALL findings + ty errors. Tests guard behavior.
2. Slug: **digital-ocean-dynamic-dns** (preserve PyPI name); patch generated repo URLs -> nivintw/ddns.
3. Release: **adopt release-please** — seed manifest 1.3.7, remove [tool.semantic_release] + old workflow.
4. PR shape: **one PR**.

## Answers (scratchpad/answers.yml): project_name "Digital Ocean Dynamic DNS"

   slug digital-ocean-dynamic-dns, pkg digital_ocean_dynamic_dns, py 3.12, year 2023, MIT, pytest only.

## Plan / checklist

- [ ] Phase 3a: run copier copy in-place (authentic .copier-answers.yml), reconcile conflicts
- [ ] Phase 3b: merge pyproject (template structure + real deps/scripts/version 1.3.7)
- [ ] Phase 3c: README/CHANGELOG keep real content + SPDX; .gitignore merge
- [ ] Phase 3d: release-please manifest=1.3.7; remove semantic_release + old workflow + licenserc.toml(old)
- [ ] Phase 3e: patch repo URLs digital-ocean-dynamic-dns -> ddns (SECURITY.md, link-check.yml)
- [ ] Phase 3f: hawkeye format SPDX headers; reuse lint clean
- [x] Phase 3 scaffold committed; A_record fn renames committed (N802 src=0)
- [~] Phase 3g: ruff fan-out workflow running (wf_9d45afee-7d7, 26 files, Sonnet/file).
  Test ignores set to idiomatic only (S101,INP001,ANN,D,ARG,FBT,S311,PLR2004,SLF001,N802,N803,N806).
  DTZ convention: datetime.now(tz=timezone.utc).astimezone() (preserve local wall-clock).
  ty: only 4 diagnostics, all in tests/subdomains/test_list_subdomains.py (mixed int|str dict) — fix after workflow.
- [ ] After workflow: verify full ruff clean + pytest green + ty clean; handle stragglers
- [ ] DISCOVERED: template release-please does NOT publish to PyPI -> added .github/workflows/publish.yml
      (ddns-specific, reuses TWINE_PYPI_UPLOAD_TOKEN). Flag in PR + to user.
- [x] Phase 3 complete: gate green (ruff/format/ty clean, 107 tests, 95.6% cov). 5 commits.
- [x] Phase 4 /simplify: HTTPStatus, SQL spaces, logger/rprint naming, logs comment, publish guard. committed.
- [x] Phase 5 docs: N/A (not a plugin/marketplace; README badges fixed). skipped.
- [~] Phase 6: /dev-kit:review-pr running
- [ ] Phase 7: install missing tools (ty/shfmt/zizmor/yamllint), uv lock, prek run --all-files
- [ ] Phase 8: draft PR Closes #16, Copilot loop, ready

## Notes

- Removed stale classic pre-commit git hooks from primary .git/hooks (broken, replaced by prek).
- Build artifacts tracked in repo? check: dist/, htmlcov/, .coverage, *.egg-info, scratch.md -> likely remove/gitignore.

## STATUS: Phase 8 — PR #17 (draft) open. Closes #16. Issue flipped to in-review.
- Gate fully green: ruff/format/ty/pytest(107, 95.6%)/prek all pass.
- Copilot review requested; iterating to convergence before `gh pr ready`.
