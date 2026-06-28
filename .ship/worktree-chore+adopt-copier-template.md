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

## Answers (scratchpad/answers.yml): project_name "Digital Ocean Dynamic DNS",
   slug digital-ocean-dynamic-dns, pkg digital_ocean_dynamic_dns, py 3.12, year 2023, MIT, pytest only.

## Plan / checklist
- [ ] Phase 3a: run copier copy in-place (authentic .copier-answers.yml), reconcile conflicts
- [ ] Phase 3b: merge pyproject (template structure + real deps/scripts/version 1.3.7)
- [ ] Phase 3c: README/CHANGELOG keep real content + SPDX; .gitignore merge
- [ ] Phase 3d: release-please manifest=1.3.7; remove semantic_release + old workflow + licenserc.toml(old)
- [ ] Phase 3e: patch repo URLs digital-ocean-dynamic-dns -> ddns (SECURITY.md, link-check.yml)
- [ ] Phase 3f: hawkeye format SPDX headers; reuse lint clean
- [ ] Phase 3g: FIX ALL ruff ALL + ty findings across src(14)+tests(21); pytest green
- [ ] Phase 4: /simplify
- [ ] Phase 5: docs (no docs site -> skip w/ note)
- [ ] Phase 6: /dev-kit:review-pr
- [ ] Phase 7: install missing tools (ty/shfmt/zizmor/yamllint), uv lock, prek run --all-files
- [ ] Phase 8: draft PR Closes #16, Copilot loop, ready

## Notes
- Removed stale classic pre-commit git hooks from primary .git/hooks (broken, replaced by prek).
- Build artifacts tracked in repo? check: dist/, htmlcov/, .coverage, *.egg-info, scratch.md -> likely remove/gitignore.
