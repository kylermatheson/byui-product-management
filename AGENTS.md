# BYU-Idaho Product Management adaptation

This repository is a Quarto book for BYU-Idaho Product Management, Winter 2027 Second Block, February 22–April 8. Professor: Rob Teigen. Teaching Assistant: Kyle Matheson. Do not call the offering a pilot. Use Codex as the primary course tool and Claude as a supported alternative.

## Current course structure

Use `00-schedule.qmd`, `00-assignments.qmd`, `_weeks.yml`, and `course-support/starter/course-schedule.json` together. There are seven weeks; Week 7 ends Thursday, April 8. Meeting days remain Mon/Wed or Tue/Thu and times remain blank. All six sprint wrap-ups are due Saturdays, February 27 through April 3; plans for Sprints 2–6 are due the preceding Saturday. Sprint 1's plan is submitted during the first class. All dated submissions close at 23:59 America/Boise. Midterm window: proposed March 12–13; final window: proposed April 5–8; delivery remains blank. Peer testing is assigned Week 6 and its video is due April 3, with feedback exchanged in class before the final build closes. Week 7 has no new sprint. Do not import university administrative deadlines.

Required reading is the seven short W01–W07 essentials guides, designed for 20–30 minutes of preparation per week. All original full chapters remain optional and accessible, with their headings and anchors preserved. Setup and building take additional time. Every guide includes Prepare for two sessions, Teach One Another, and Ponder and Prove. Keep faith integration and AIRE. Retain six sprints, peer testing, both exams, the 450-point model, and existing 5-point optional extra credit. Exams assess required essentials and explicitly taught material; full-source practice topics do not independently add requirements. No new graded quizzes, posts, essays, or classroom worksheets.

Original course information and historical guidance are preserved in `_source-original/source.tar.gz` with a manifest. Never modify the snapshot or include it in published output. Use `99-credits.qmd` for source attribution and retained copyright notices. Historical BYU staffing, contacts, funding, course numbers, dates, and deployment instructions are not current course facts.

## Student support

`00-course-workflows.qmd` describes portable procedures in `course-support/starter/`. They work as plain-text prompts in either agent, without external skill refreshes. After changing starter files, run `python3 scripts/build-course-starter.py`. Tool-specific instructional examples may remain Claude-specific; do not change command names by search-and-replace.

## Working discipline

Use the `byui-seven-week` adaptation branch as requested. Preserve unrelated working-tree changes, including the user's untracked `AGENT.md` and deletion of `CLAUDE.md`. Stage and commit explicit paths only. Do not push, merge, or publish without an explicit request. The GitHub Actions workflow publishes the rendered `_book/` artifact from `byui-seven-week`, following the requested branch deployment. Pages must use GitHub Actions as its source, and the github-pages environment should allow only this deployment branch. Do not use the repository root as a Pages publishing folder.

Keep `quarto preview` available during edits and run a full `quarto render` before finishing navigation or cross-reference changes. Inspect the site in a browser. Run `python3 scripts/check-seven-week-course.py` and the navigation/button tests when changing their behavior. Keep chapter names and anchors stable. Use plain factual language, no em dashes or decorative emoji in new copy. Do not rewrite unrelated instructional material.
