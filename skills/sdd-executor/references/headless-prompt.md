# Headless / unattended prompt (one task per fresh session)

Used by `scripts/run-tasks.sh`, which reads the fenced block below and substitutes `<FEATURE_DIR>`, `<TASK-ID>`, `<BRIEFS_DIR>`, `<GIT_BASE>` (a pre-run tree snapshot the script takes before each task) and `<COMMIT_POLICY>`. Keep placeholders exactly as written.

```text
Read the project's instruction files (CLAUDE.md, AGENTS.md or equivalent) and obey
their rules. Then read <FEATURE_DIR>/spec.md, plan.md, tasks.md and progress.md.
Implement ONLY task <TASK-ID>; do not touch other tasks.

Process:
1. If the task says Owner: human, do nothing else: write "Blocked: <TASK-ID>" in
   progress.md stating what the human must do, and exit. A Type: env-validation
   task with Owner: agent runs as written; if it fails, write "Blocked: <TASK-ID>"
   with the evidence and the exact spec change proposed, and exit.
2. If it says Tests: none (<reason>) or its Covers has no AC#/E#, skip this step. Otherwise delegate to the
   `test-writer` subagent for failing tests; confirm they fail for the right reason.
   Record `git hash-object` of each new test file.
   If the new tests are wrong (not the implementation), re-run test-writer only
   with a written diagnosis, re-record the hashes and tell the reviewer "tests
   corrected by test-writer after round N (reason)". Any other test change: block.
3. Implement the minimum that satisfies the tests, following plan.md. Never invent
   formats or identifiers the plan did not pin: write "Blocked: <TASK-ID>" with the
   exact plan change proposed.
4. Run the verify commands the project defines.
5. Re-check the test-file hashes (any change means stop and block). Delegate to a
   fresh `spec-reviewer` subagent (mode task, Rigor standard) with the task ID, document paths,
   verify commands, `Git base: tree <GIT_BASE>`, `Base kind: pre-run` (taken before
   this run, so the new test files appear in the diff as expected; the head is the
   working tree, untracked files included) and the test-file list. The hash
   comparison of step 5 replaces the reviewer's "unchanged since base" check. Never
   give it progress.md or your reasoning.
6. On FAIL, fix and repeat 4-5. Maximum 3 fix rounds after the initial review. If
   the same failure appears twice, or the cap is hit, stop: write the attempts
   under "Blocked: <TASK-ID>" in progress.md and exit.
7. On PASS: tick the task in tasks.md and update progress.md (Completed, Decision,
   Follow-ups, Learnings). <COMMIT_POLICY>

Rules:
- Never push, merge, deploy or touch secrets.
- Never weaken, skip, comment out or delete tests; do not edit spec.md or plan.md.
- No scope expansion: ideas outside the task go to progress.md under Follow-ups.
- Build subagent briefs by filling the templates in <BRIEFS_DIR>; if any
  <placeholder> remains, do not launch.
- On ambiguity or anything that changes behavior, do not guess: write
  "Blocked: <TASK-ID>" with the question and exit.
```

`<COMMIT_POLICY>` is substituted by the script: with `SDD_COMMIT=1`, "Commit on the current branch with the task ID in the message (the user opted in to commits for this run)."; otherwise, "Do not commit: leave the changes in the working tree and print the suggested commit message (project convention, containing the task ID)."

Why this form: file paths instead of pasted content keep the prompt short and the files authoritative; the blocker protocol, stuck detection and iteration cap prevent loops that "solve" problems by cheating; commits are opt-in because the history belongs to the user.
