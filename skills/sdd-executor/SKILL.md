---
name: sdd-executor
description: Executes an approved feature's tasks.md (one task, one milestone, or all) with tests first, independent review and human checkpoints, resuming from progress.md. Explicit invocation only - run it as /sdd-executor <feature folder> [T# | M# | all] after spec, plan and tasks are approved.
disable-model-invocation: true
argument-hint: "[feature folder] [T# | M# | all] [--light]"
---

# sdd-executor

Execute `tasks.md` of an approved feature, one task at a time: failing tests first, minimal implementation, verify commands, an independent review, then a human checkpoint at every milestone. State lives in files (`tasks.md` ticks, `progress.md`), never only in the chat, so the run is resumable in a fresh session.

**Explicit-only.** This skill starts only when the user types `/sdd-executor <feature folder> ...` themselves; `disable-model-invocation` means the model cannot launch it. If the user says "go", "run it" or "start" in chat, do not try to start it: tell them to type the command. Why: running code changes autonomously is a decision the human must take with an explicit act, and a chat "go" is too easy to misread.

Why this shape: "done" must come from tests and reviewer evidence rather than from the implementer's opinion; the reviewer and the test writer are independent of the implementer; and the human keeps intent and final review.

## Arguments

`$ARGUMENTS` = `<feature folder> [T# | M# | all] [--light]`.

- Feature folder: a path to the folder holding `spec.md`, `plan.md`, `tasks.md`, `progress.md`. If missing or ambiguous, list the candidate folders found by discovery and ask.
- Scope: `T3` (one task), `M2` (one milestone; `M#` is the id in parentheses in the milestone heading, and the wave table in `tasks.md` may be reused for waves), `all` (everything unchecked). Default when omitted: the next milestone that has unchecked tasks. Always skip tasks already ticked; `progress.md` tells you where the last session stopped. Waves are computed within a milestone, never across milestones.
- `--light`: the reviewer reports only blockers and majors (pass `Rigor: light` in its brief). The reviewer returns only `known minors: N`; record that line under `progress.md` Follow-ups. Minors never trigger fix rounds; the cap stays 3. Without the flag, behavior is unchanged (`Rigor: standard`). Why: low-risk features should not burn rounds on nits.

## 0. Discovery

Follow `references/discovery.md` (read it now). You need from it: instruction files and their rules, specs dir, verify commands (test / lint / typecheck / build / verify-all), test conventions and runner, commit convention, documentation language. Rules found in the project's instruction files (for example "consult versioned docs before using library X") bind you during implementation.

## 1. Preflight (stop on the first failure and say what is missing)

1. `spec.md`, `plan.md`, `tasks.md` exist and the Status line, which is the first line of each, reads `Status: Approved (<user>, <date>)`. A Draft document, or a legacy document with no Status line (treat as Draft), stops the run unless the user explicitly overrides in chat; record each override in `progress.md` (Decision) and in the `Overrides` header line of `tasks.md`. Read `Overrides` too: a recorded override is not asked twice.
2. `spec.md` has no unresolved `Q#`: every `Q#` reads `Qn: ... -> RESOLVED (<date>): ...`, or the section says `None`. An unresolved question means the document is not really approved.
3. Current branch is not the repository's default branch. If it is, offer (via `AskUserQuestion`) to create a feature branch or a git worktree, recommending the branch; do the work only after the answer.
4. Working tree is clean, or the user confirmed that the existing changes are not part of this run. Record the paths of pre-existing changes in `progress.md` (Decision) so reviews can exclude them.
5. Verify commands are resolved and each is confirmed to exist (script present, binary on PATH). A missing check is reported and either marked `manual` by the user or created by an explicit task; never invented.
6. The global subagents `test-writer` and `spec-reviewer` are available (listed in the Agent tool's agent types). If not, stop: they are installed under `~/.claude/agents/`.
7. Read `spec.md`, `plan.md`, `tasks.md`, `progress.md` in full. Compute the waves (see section 2).
8. Record the run base in `progress.md` (Decision), once per run: `Base: HEAD <sha>` and, if the tree is dirty, `Base tree: <T0>` from the snapshot command in section 3. The `final` review needs a real base, and the reviewer must not have to guess what you changed.
9. Print a 5-line summary (goal, non-goals, tasks/waves in scope, first task, verify command) and **wait for the user to answer "go"**. Do not touch code before that. Exception: if the user explicitly said to run without milestone stops (e.g. "go, no milestone stops"), skip this wait and the milestone `AskUserQuestion` of section 4, still write each milestone report to `progress.md`, and record that instruction in `progress.md` (Decision). Hard stops (Blocked, `Blocking: yes` human tasks, failed `env-validation`) still stop.

## 2. Scheduling

- **Sequential by default**, in `tasks.md` order, respecting `Depends on`.
- **Parallel only** when all hold: the tasks are `Parallel: yes`, in the same wave (all their dependencies are done), and their `Files` do not overlap. Each runs through the `Agent` tool with `isolation: "worktree"`, at most **3 concurrent**. Subagents cannot spawn subagents, so:
  1. The main session runs the `test-writer` step for the whole wave first and records the hash of each new test file (section 3, step 2).
  2. Each worktree agent receives the paths of its task's new test files and copies them in unchanged, then implements and runs verify. It must not edit those tests.
  3. Temporary internal commits are allowed only inside the throwaway worktree branches; say so in the pre-wave confirmation. Nothing lands on the user's branch history unless they asked for commits.
  4. Merge back **one worktree at a time** with `git merge --no-commit` (or `--squash`), snapshot the tree before and after, run the full verify, then run the reviewer step from the main session on that diff. A failing merge goes through the same fix loop as a failing task.
- Before the first parallel wave, show the user the estimated cost (agents x tokens), the merge-conflict risk (shared files, shared config/lock files) and the temporary-commit note above, and ask for confirmation. If in doubt, stay sequential: parallelism multiplies cost.
- **`Owner: human`** (manual-only) tasks, never attempted by you. Read `Blocking:`:
  - `Blocking: yes`: stop, state exactly what the human must do and which observable result closes it, and wait. Tick only on their confirmation.
  - `Blocking: no`: record it in `progress.md` as `Deferred: T# - <what the human must do>`, leave it unticked, and continue with agent tasks that do not depend on it (tasks that depend on it stay pending). It reappears in the final "Unverified risk" list.
- **`Type: env-validation`** tasks check an environment assumption (spec `A#` / `[ENV]` criteria) before dependents rely on it. Run them as written, unattended when `Owner: agent`; only `Owner: human` ones wait for a person. If one fails: stop, write `Blocked: T#` with the evidence, and propose the exact spec change (the human reopens the spec). Do not code around it.

## 3. Per-task loop

Context for each task is spec + plan + this task only. Delegation happens from this session because subagents cannot spawn subagents.

1. **State** the task ID, its `Covers:` and its `Done when`.
2. **Tests first.** If the task says `Tests: none (<reason>)` (reason: docs-only | infrastructure | hardware-glue | manual) or its `Covers` has no `AC#`/`E#`, skip the test-writer and the failing-test check (an explicit `Tests: none (...)` wins even when `Covers` lists criteria, e.g. the final verify task); the `Done when` check and the review still apply. Otherwise delegate to `test-writer` with the brief built from `references/briefs/test-writer-brief.md` (see "Briefs" below). Pass IDs and paths, never your design ideas. Confirm that the new tests fail for the right reason (missing behavior or symbol, not a syntax or setup error). A criterion the writer reports as untestable goes to the user, not to a guess. Then freeze the tests and the diff base so the review can prove nothing changed them:
   - `git hash-object <file>` for each new/modified test file; keep the list.
   - Snapshot tree (does not touch the real index; includes untracked files and any pre-existing changes, so those drop out of the review diff): `T=$(IDX=$(mktemp -u); GIT_INDEX_FILE=$IDX sh -c 'git read-tree HEAD && git add -A && git write-tree'; rm -f "$IDX")`. Record `T` and the hashes in your notes (not in a file the reviewer reads).
   **Test-correction sub-step.** If the tests are wrong (not the implementation), you may re-run `test-writer`, only with a written diagnosis (which test, what it asserts, why that contradicts the criterion or plan). Re-hash the test files, record the new hashes, and tell the reviewer in the brief: "tests corrected by test-writer after round N (reason)". Any other change to the tests still stops the run. Why: a wrong test is a defect too, but only the independent writer may fix it.
3. **Implement** the minimum that satisfies the tests, following `plan.md` and the project's conventions. Do not invent observable formats or identifiers (message text, field names, file formats, ids, units) the plan did not pin: if the task depends on an unpinned detail, stop and propose the exact plan change (or a `Q#`). Only if the user explicitly tells you to decide, record the decision in `progress.md` (Decision) and put it in the brief's `User-ordered decisions` field. Touch only the task's `Files` (plus what is strictly needed; mention extras in progress.md).
4. **Verify.** Run the verify commands. Fix until green or the cap in step 6.
5. **Independent review.** First re-run `git hash-object` on the test files: if any hash changed, stop, because tests changed outside the test-writer step; tell the user. Then take a second snapshot `T2` the same way and delegate to a fresh `spec-reviewer` in `task` mode with the brief built from `references/briefs/reviewer-task-brief.md`: task ID, paths to spec/plan/tasks (never `progress.md`), verify commands, `Rigor`, `Git base: tree <T>`, `Base kind: post-test snapshot`, `Git head: tree <T2>`, the test-file list, and paths of pre-existing changes to exclude. Never include your reasoning, your summary of the change, or what you think is risky.
6. **FAIL** -> fix blockers and majors (with `--light`, only those; record `known minors: N` under Follow-ups), repeat steps 4-5 with fresh snapshots. **Maximum 3 fix rounds after the initial review.** Stuck detection: if the same failure appears twice, or the cap is hit, stop retrying: append the attempts and the current failure as a `Blocked: T#` entry in `progress.md` and ask the user (`AskUserQuestion`: guidance / revise task / skip / stop). When the user unblocks it, rewrite that entry as `Resolved: T# - <how>` (the unattended script counts `Blocked:` lines).
7. **PASS** -> tick the task in `tasks.md`; append to `progress.md` under the template's sections: `Completed` (T#, what changed), `Decision` (deviations from the documents and why), `Follow-ups` (out-of-scope ideas), `Learnings` (gotchas). **Commit only if the user asked for commits** (in the invocation or in chat), using the project's commit convention with the task ID. Otherwise do not commit; print a suggested commit message containing the task ID and let the user commit.

### Briefs

Build the `test-writer` and `spec-reviewer` briefs from the template files in `references/briefs/` (`test-writer-brief.md`, `reviewer-task-brief.md`, `reviewer-final-brief.md`), not by hand: copy the file, fill every `<placeholder>` and nothing else. The only allowed additions to a reviewer brief are its `Test corrections` and `User-ordered decisions` template fields. Before launching, verify no `<...>` placeholder remains; a leftover aborts the launch. Why: hand-written briefs drift and leak implementer opinions.

Independence caveat: a brief you author can hide ambiguity from the reviewer (a criterion you read one way, a detail you filled in). Keep a private list of the choices you took while writing briefs and list them in the final report under "Decisions the orchestrator took in briefs". Never pass that list to the reviewer.

Review batching (`Review: batch`) exists only as an option for tasks of at most 1 file, and only if the user asks for it and approves it. Default: one fresh reviewer per task.

Reading verdicts critically: in the first tasks, inspect what the reviewer actually checked. If everything passes with thin evidence (no `file:line`, no command output), tighten the brief (name the criteria and edge cases explicitly, ask for the failing-assumption check) and re-run before accepting. A reviewer that approves everything is a defect in the brief.

## 4. Milestone checkpoint

After the last task of a milestone (marked `MILESTONE CHECKPOINT` in `tasks.md`), stop. Produce the report from `references/milestone-report.md`: tasks done, verify results, reviewer findings, deviations, open questions, diff stat. Then `AskUserQuestion` (skipped in an autonomous run, where the report is only written to `progress.md`) with: **continue** / **adjust tasks** / **stop**. Suggest continuing in a fresh session (`/clear` or a new session), since context rot degrades quality and `progress.md` carries the state. "Adjust tasks" means: propose the exact edit to `tasks.md` and wait for approval before applying it.

## 5. Hard rules

- Never weaken, skip, comment out or delete tests. Tests change only in the `test-writer` step (including the test-correction sub-step with a written diagnosis). Any other test change stops the run: tell the user why.
- Never edit `spec.md` or `plan.md`. If they are ambiguous, contradictory or wrong, stop and propose the exact change for approval.
- No scope expansion. Ideas outside the task go to `progress.md` under Follow-ups.
- Never push, merge to the default branch, deploy, or touch secrets without an explicit request. Never open a PR or issue unless asked.
- Prefer asking over guessing on anything that changes behavior.
- Do not disable hooks, linters or checks to get green.

## 6. Finish

When all tasks in scope are done (or the user stops at a milestone and wants a wrap-up):

1. Run the full verify-all command (and build if the project defines one).
2. Delegate to one final `spec-reviewer` in `final` mode over the whole feature diff (base = the `Base tree` or `Base: HEAD` recorded in `progress.md`, or the commit the feature branched from; paths of pre-existing changes excluded; never pass `progress.md`). Ask for the AC coverage matrix. Any `missing`/`partial` row or blocker/major finding reopens work: report it and ask. `manual` and `deferred` rows go to the Unverified risk list.
3. Drift control: compile the deviations yourself from the `Decision` entries of `progress.md`, then list the proposed updates to `spec.md`, `plan.md` and project docs (architecture, data/contract docs, README) implied by what was built, as exact changes. Wait for approval; apply nothing yourself unless approved.
4. Summarize: tasks done, verify results, matrix, deviations, follow-ups, suggested commit messages if not committed, plus two lists:
   - **Unverified risk**: every `Deferred` human task, every manual-verification row not yet confirmed, and each `[ENV]` assumption not yet validated. Never declare the feature done while any such row is unverified; say "implemented, not verified" instead.
   - **Decisions the orchestrator took in briefs** (from your own brief choices; never given to the reviewer). Do not create a PR or issue unless asked.

## Resuming

A new session re-reads the four documents; ticked tasks and `progress.md` entries are authoritative, and the recorded `Base` is reused rather than re-taken. If a `Blocked: T#` entry exists, show it first and ask how to proceed before continuing.

## Optional unattended mode (off by default)

`scripts/run-tasks.sh` runs one headless session per task using `references/headless-prompt.md`. Use it only after the interactive flow has proven stable on a real feature (reviewer verdicts audited, briefs tuned), on a branch or worktree, with caps. Never start it unless the user asks for it. It does not commit unless `SDD_COMMIT=1`, requires `SDD_ALLOWED_TOOLS` (so verify commands can run), and never pushes.

## Files

- `references/discovery.md` - shared project discovery procedure.
- `references/orchestrator-prompt.md` - the interactive process prompt and brief rules.
- `references/briefs/` - brief templates: `test-writer-brief.md`, `reviewer-task-brief.md`, `reviewer-final-brief.md`.
- `references/headless-prompt.md` - one-task unattended prompt.
- `references/milestone-report.md` - report template.
- `scripts/run-tasks.sh` - optional outer loop.
- `references/examples.md` - worked example of discovery on a concrete project (reference only).
