# BYU-Idaho Product Management adaptation

This repository is a Quarto book for BYU-Idaho Product Management, Winter 2027 Second Block, February 22–April 8. Professor: Rob Teigen. Teaching Assistant: Kyle Matheson. Do not call the offering a pilot. Use Codex as the primary course tool and Claude as a supported alternative.

## Current course structure

Use `00-schedule.qmd` and `_weeks.yml` together as the weekly source of truth. There are exactly seven weeks; Week 7 ends Thursday, April 8. Do not infer class meeting days, exact assignment deadlines, exam windows, or additional administrative deadlines from these weekly ranges. Unknown course details stay labeled blanks. Keep all readings, outcomes, rubrics, six sprints, peer testing, both exams, and the 450-point model. Sprints 1–5 last one week and Sprint 6 spans Weeks 6–7. Keep faith integration and the AIRE framework.

Original course information and historical guidance are preserved in `_source-original/source.tar.gz` with a manifest. Never modify the snapshot or include it in published output. Use `99-credits.qmd` for source attribution and retained copyright notices. Historical BYU staffing, contacts, funding, course numbers, dates, and deployment instructions are not current course facts.

## Student support

`00-course-workflows.qmd` describes portable procedures in `course-support/starter/`. They work as plain-text prompts in either agent, without external skill refreshes. After changing starter files, run `python3 scripts/build-course-starter.py`. Tool-specific instructional examples may remain Claude-specific; do not change command names by search-and-replace.

## Working discipline

Use the `byui-seven-week` adaptation branch as requested. Preserve unrelated working-tree changes, including the user's untracked `AGENT.md` and deletion of `CLAUDE.md`. Stage and commit explicit paths only. Do not push, merge, or publish without an explicit request. The GitHub Actions workflow publishes pushes to main and should not be expanded for this branch.

Keep `quarto preview` available during edits and run a full `quarto render` before finishing navigation or cross-reference changes. Inspect the site in a browser. Run `python3 scripts/check-seven-week-course.py` and the navigation/button tests when changing their behavior. Keep chapter names and anchors stable. Use plain factual language, no em dashes or decorative emoji in new copy. Do not rewrite unrelated instructional material.
