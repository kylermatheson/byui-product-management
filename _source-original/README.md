# Original source snapshot

`source.tar.gz` contains every tracked file from the source commit recorded in `manifest.json`, exported directly with `git archive`. The archive preserves original course information, copyright notices, policies, release notes, and tool instructions. It excludes working-tree changes and untracked files. Extract it into a separate directory to inspect it.

This directory must never be included in the rendered or deployed course site.
