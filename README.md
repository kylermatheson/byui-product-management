# BYU-Idaho Product Management

Winter 2027 Second Block: **February 22–April 8, 2027**. Professor: **Rob Teigen**. Teaching Assistant: **Kyle Matheson**. Codex is the primary tool; Claude is a supported alternative.

The course has seven short weekly essentials guides, designed for **20–30 minutes of preparation per week**, with two class sessions organized around **Prepare, Teach One Another, and Ponder and Prove**. All full chapters remain available as optional references. Setup, building, and homework take additional time.

All six sprint wrap-ups are due Saturdays, February 27 through April 3. Plans for Sprints 2–6 are due the preceding Saturday; Sprint 1's plan is submitted during the first class. Dated submissions close at 11:59 p.m. America/Boise. Week 7 is the showcase, reflection, and final exam. Proposed exam windows are March 12–13 and April 5–8; delivery details and exact meeting days/times remain unconfirmed. The 450-point grading model and existing optional extra credit are unchanged.

Start with `00-schedule.qmd` for class activities and `00-assignments.qmd` for submissions and dates. `course-support/starter/course-schedule.json` records the same dates for the portable student procedures. The calendar supplies only the block dates and weekly ranges.
## Preview and validate

Install Quarto and Python. For the retained Python examples, install the build dependencies in a virtual environment and select that interpreter:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export QUARTO_PYTHON="$PWD/.venv/bin/python"
```

On Windows, use `.venv\Scripts\python.exe` and set `QUARTO_PYTHON` to that interpreter in PowerShell.

```sh
quarto preview --no-browser --port 4200
```

Open http://localhost:4200/. Before finishing changes:

```sh
python3 scripts/build-course-starter.py
quarto render
python3 scripts/check-seven-week-course.py
```

Run the JavaScript behavior checks with Node.js:

```sh
node --test scripts/tests/course-navigation.test.mjs
```

The same test file can run with Deno using its Node compatibility support: `deno test --allow-read scripts/tests/course-navigation.test.mjs`.

`00-schedule.qmd` and `_weeks.yml` must agree. `00-course-workflows.qmd` documents the portable student procedures, and `course-support/starter/` is the source for the downloadable starter zip.

## Source preservation

`_source-original/source.tar.gz` contains the unchanged tracked source at the commit recorded in its manifest. It preserves the original course information and release history and is excluded from publication. See `99-credits.qmd` for authorship and copyright attribution, and `AGENTS.md` for current repository guidance.

Work on `byui-seven-week`. Do not push, merge, or publish as part of the adaptation. The existing workflow publishes pushes to `main`.
