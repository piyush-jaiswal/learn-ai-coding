---
description: Stage changes, wait for user approval, commit, then rebase on origin/master
---

Stage the current project changes, wait for the user to approve them, then commit and sync with the remote.

1. Inspect `git status --short`. If the working tree is clean, report that there is nothing to commit and skip to step 5.
2. Stage all project changes with `git add -A`. Do not use `git add -f`; ignored files must stay ignored.
3. Show the staged changes by printing `git diff --cached --stat` and the full `git diff --cached` output directly in your reply as fenced code blocks, not only as tool output. Then ask the user to approve the commit. Do not commit until the user explicitly approves. If they request changes, make them, re-stage, and show the updated diff.
4. Commit through the `commit_changes` tool with this message: $ARGUMENTS. Direct `git commit` is denied by the project permissions. If the message above is empty, ask for a commit message and stop.
5. Run `git pull --rebase origin master` and report the outcome. If the rebase hits conflicts, stop and report the conflicted files; do not resolve them silently or abort the rebase without explaining why.
