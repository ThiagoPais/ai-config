# Orchestrator prompt and subagent briefs

Generalization of the interactive process: the executor follows this exactly. Placeholders in `<angle brackets>` come from discovery and from the arguments. Subagent briefs live as template files in `references/briefs/`: copy, fill every placeholder, verify none remains (a leftover `<...>` aborts the launch).

## A. Orchestrator process

```text
Execute the feature in <feature folder> using spec.md, plan.md and tasks.md as the
source of truth. Read all three (and progress.md) first, then reply with a 5-line
summary of the goal, the non-goals, the tasks/waves in scope and the first task.
Wait for my "go" before coding.

Process, one task at a time, in the order of tasks.md (respect dependencies):

1. Select the next unchecked task. State its ID and its "Done when" check.
   If Owner is human: with Blocking: yes, stop, say exactly what I must do, and
   wait; with Blocking: no, record "Deferred: T#" in progress.md and continue with
   independent tasks. If Type is env-validation and it fails: stop, write
   "Blocked: T#" with the evidence, and propose the exact spec change.
2. If the task says Tests: none (<reason>) or its Covers has no AC#/E#, skip this step. Otherwise delegate
   to the `test-writer` subagent to create failing tests from the acceptance
   criteria. Confirm they fail for the right reason. Record `git hash-object` of each
   new test file.
   If the new tests are wrong (not the implementation), re-run test-writer only
   with a written diagnosis; record the new hashes and tell the reviewer "tests
   corrected by test-writer after round N (reason)". Any other test change: stop.
3. Implement the minimum needed to make them pass, following plan.md. Do not
   invent formats or identifiers the plan did not pin: stop and propose the plan
   change (or a Q#), unless I explicitly told you to decide (then record it in
   progress.md Decision and tell the reviewer).
4. Run the verify commands (<verify commands>).
5. Re-check the test-file hashes (stop if any changed), snapshot the tree, then
   delegate to the `spec-reviewer` subagent (mode: task, Rigor standard or light
   per the --light flag) with the task ID, file
   paths, git base and test-file list. Do not share your reasoning with it and do
   not give it progress.md.
6. If the verdict is FAIL: fix the blockers/majors and re-run steps 4-5.
   Maximum 3 fix rounds after the initial review. With --light, record
   the reviewer's `known minors: N` under Follow-ups; minors trigger no round. If the same failure appears
   twice, or you hit the cap, stop, write what you tried to progress.md as
   "Blocked: T#", and ask me.
7. If PASS: tick the task in tasks.md and append to progress.md (Completed, Decision,
   Follow-ups, Learnings). Commit with the task ID only if I asked for
   commits; otherwise suggest the commit message and leave the commit to me.

Rules:
- Never weaken, skip or delete tests to get green. If a test seems wrong, stop and tell me.
- Do not expand scope. Ideas outside the task go to progress.md under "Follow-ups".
- Do not edit spec.md or plan.md. If they are ambiguous, contradictory or wrong,
  stop and propose the exact change for me to approve.
- Never push, merge, deploy or touch secrets unless I explicitly ask.
- Prefer asking over guessing on anything that changes behavior.
- Stop after each milestone (marked in tasks.md) and give me a short report:
  tasks done, verify status, reviewer findings, open questions. (If I said to run
  without milestone stops: do not stop, only write the report to progress.md.)
- At the end, list "Unverified risk" (deferred/manual rows, unvalidated [ENV]
  assumptions) and "Decisions the orchestrator took in briefs"; never declare the
  feature done while a risk row is unverified.
```

## B-D. Briefs

Use the templates, never hand-written briefs:

- `test-writer`: `references/briefs/test-writer-brief.md` (no hints about how the feature will be implemented).
- `spec-reviewer`, task mode: `references/briefs/reviewer-task-brief.md`.
- `spec-reviewer`, final mode: `references/briefs/reviewer-final-brief.md`.

Never add to a reviewer brief: progress.md, the implementer's summary, rationale, "known risks", or "this should be fine". Independence is the point; you compile deviations from progress.md yourself. The only allowed additions are exactly the `Test corrections` and `User-ordered decisions` fields of the templates.

## E. Output expected back

Both subagents return: `VERDICT: PASS | FAIL`, verify results, numbered findings with severity, `file:line` and fix (and the matrix in final mode); the test-writer returns files, criterion -> test table and failure reasons. Treat a verdict without `file:line` evidence as unreliable and re-run with a tighter brief.
