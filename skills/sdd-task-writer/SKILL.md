---
name: sdd-task-writer
description: Break an approved spec.md and plan.md into small, ordered, verifiable work items, writing tasks.md (T# tasks grouped into milestones, with Covers, Depends on, Files, Done when, Parallel, Owner, Blocking) plus an empty progress.md. Use whenever the user says "break this into tasks", "create tasks.md", "split the plan into steps", "make a task list for this feature", "slice the plan", "sdd tasks", or passes a feature folder that has an approved plan.md but no tasks.md, even if they do not say "SDD". Also use to revise an existing tasks.md after the plan changed.
argument-hint: "[feature folder]"
---

# SDD task writer

Turn an approved plan into `tasks.md`: the ordered, independently verifiable steps that an executor (human or agent) can run one fresh session at a time. Also create an empty `progress.md`, the running log that carries state between sessions.

Why this matters: a task without a concrete "Done when" is the usual root cause of weak validation, and oversized tasks hide bugs. Everything below exists to make each task small, checkable and traceable back to the spec.

Feature folder: `$ARGUMENTS`. If empty, run discovery (below) and ask which folder under the specs directory to use, proposing the one with an approved `plan.md` and no `tasks.md`.

## Step 0: Prerequisites (stop if unmet)

1. Run the discovery procedure in `references/discovery.md` (read-only). It yields the specs directory, verify commands, test conventions, commit style and documentation language.
2. Confirm `spec.md` and `plan.md` exist in the feature folder and both have `Status: Approved (...)` as their first line (a missing Status line counts as Draft). If either is missing or Draft, stop and list what blocks. Continue only if the user explicitly overrides, and record the override on the `Overrides:` header line of `tasks.md`.
3. If `spec.md` has any `Q#` that is not marked RESOLVED, stop: unresolved questions make tasks guesswork.
4. If `tasks.md` already exists, switch to update mode: propose a diff and never overwrite; keep ticked tasks and their IDs stable. If the file was Approved, set it back to `Status: Draft` after applying: a changed task list needs a new approval (ticked tasks stay ticked). Note that the executor's in-flight work may be affected, and list stale-downstream items if any exist.

Documents upstream of tasks are read-only here. If the spec or plan is wrong or ambiguous, propose the exact change and wait; do not patch it silently or work around it in a task.

## Step 1: Read

Read `spec.md` (goals, non-goals, `AC#`, `E#`, `## Assumptions` `A#`, criteria marked `[ENV]`, constraints), `plan.md` (decisions `D#`, components and files touched, Traceability section with its optional "Also" column, "Environment assumptions validation", "Bring-up and safe first run", "Manual verification procedures", pinned observable formats and interfaces, testing strategy, verify commands, documentation impact, sources) and the project's test layout from discovery. Tasks come from the plan's file list and Traceability section; anything not in the spec's goals does not become a task.

## Step 2: Slice

Cut the work into vertical, testable steps. Each task is one focused session, one commit, roughly 5 files or fewer, and leaves the project in a passing state. Read `references/task-sizing.md` for sizing heuristics, splitting patterns and worked cases, especially when a task feels too big or when you are unsure how to group work.

## Step 3: Write each task

Use the format in `templates/tasks.md`. Every task has:

- `T#` and a short title (imperative, one outcome).
- **Covers:** the `AC#`/`E#` it moves forward (infrastructure tasks may cover none but must say what they unblock).
- **Depends on:** task IDs or `none`.
- **Files:** concrete paths from the plan; mark `new`. Include the test files.
- **Done when:** a runnable command (taken from the discovered verify commands, never invented) AND an observable condition. Example shape: "`<test command> <path>` passes, and <what can be seen or queried>". If no command can check it, say how a human checks it and mark the check `manual`.
- **Parallel:** `yes | no`.
- **Owner:** `agent | human`. Human means deployments, migrations against shared environments, secrets, console or other manual steps, and any task whose only check is `manual`; word the task as exact instructions for the person.
- **Blocking:** `yes | no`, on every `Owner: human` task. `no` means later independent agent tasks may proceed while it is pending; `yes` means its dependents wait. Make agent tasks depend on a human task only when it truly blocks them (why: needless dependencies stall the whole run on a person).
- **Type:** optional; `env-validation` for the early task that validates an environment assumption (see Step 4).
- **Tests:** every task that covers an AC/E lists its test files among `Files`. Otherwise write `Tests: none (<reason>)` with reason exactly one of `docs-only`, `infrastructure`, `hardware-glue`, `manual`; the executor skips test-writer for it (why: there is no criterion to write a failing test from). `hardware-glue` is the only reason allowed on a task that covers an AC: it needs a one-line justification (why automation is impossible) and a `manual` Done-when that points at the plan's manual verification procedure by name. A `Type: env-validation` task that covers an AC may also write `Tests: none (manual)` (its Done when is the plan's validation row).

### Undecided-detail guard

If a task's "Done when" or `Files` depends on an observable format or identifier (message text, file name, key, schema value, port, command output) that the plan does not pin, stop and list it for the human: return to plan-writer, or raise a `Q#` in the spec. Never invent it in `tasks.md` (why: a guessed format becomes an untraceable decision that the executor then enforces).

### Computing waves and `Parallel`

A wave is a set of tasks that could run at the same time. Compute waves within each milestone, never across them: the executor stops at every milestone checkpoint, so cross-milestone parallelism does not exist. A dependency on an earlier milestone counts as already satisfied.

1. Wave 1 of a milestone is every task whose dependencies are all outside it (or `none`).
2. Wave N is every task whose in-milestone dependencies all sit in earlier waves of that milestone.
3. A task is `Parallel: yes` only when its wave holds at least one other task, no two of them share any path in `Files`, and no unfinished dependency exists (true by construction). Otherwise `no`.
4. If two or more same-wave tasks share a path, all tasks involved in that overlap are `no` and run sequentially in ID order; tasks that overlap nothing stay `yes`.

Print the waves in `tasks.md` (section "Execution waves", one row per milestone and wave, see the template) and in your summary. The executor uses them for scheduling and for the cost/merge-conflict warning before parallel work.

## Step 4: Milestones

Group tasks into milestones `M#` that each leave something demonstrable, and end every milestone with the exact line:

`> MILESTONE CHECKPOINT: stop and report to the human.`

Typical order, adapted to what the plan needs (drop empty groups):

1. Foundations: scaffolding, configuration, test harness.
2. Data and contracts: schemas, types, interfaces, migrations.
3. Logic: domain and business rules.
4. Interface: screens, endpoints, commands.
5. Validation and docs sync: full verify, end-to-end checks, and one docs-sync task covering ONLY the plan's documentation-impact rows marked `task`. Rows marked `needs separate approval` never become tasks: list them in the summary and under an "Out of tasks (needs approval)" section of `tasks.md`.

Env validation comes first. For each row of the plan's "Environment assumptions validation", emit a `Type: env-validation` task in the FIRST milestone, before any logic that depends on it; `Owner: human` or agent depending on who can run the check. Its `Done when` is the row's observation, and the task states that failure reopens the spec: stop and propose the exact spec change (why: logic built on a false assumption is wasted work).

Human tasks and the final milestone: later agent tasks may proceed past a `Blocking: no` human task. The final verify milestone must then list every still-unverified human row under "Deferred / unverified", and the feature is not "done" until those are verified. Do not hide a pending `Blocking: no` task behind a green verify.

Bring-up: when the plan has a "Bring-up and safe first run" section, add the matching `Owner: human` task (prerequisites line naming what must exist before the first run), and ensure the README/docs task covers the environment prerequisites.

Milestones are review batches for the human, so keep them to roughly 3 to 6 tasks.

## Step 5: Test-harness gap rule

For every layer the plan touches, check from discovery that a runnable check exists. If none does, add an early task (in Foundations) that creates the harness with the project's own framework, or mark the dependent "Done when" checks `manual` with explicit instructions. Never leave a layer verifiable only by "looks right".

## Step 6: Coverage self-check (fix before showing)

- Every `AC#` and `E#` is covered by at least one task; append the AC/E to task matrix (see template) with a "Verified by" level: `auto` (test or command), `manual` (human procedure) or `deferred` (pending `Blocking: no` human task). An uncovered item means a missing task or a spec gap to raise.
- Every plan row of "Environment assumptions validation" has a `Type: env-validation` task in M1; every `[ENV]` criterion is covered by one.
- Every `Owner: human` task has `Blocking`; every `Tests: none` has an allowed reason; nothing depends on an unpinned format (guard above).
- Waves are computed per milestone.
- No task lacks a `Done when`, `Files`, `Covers`, `Depends on`, `Parallel` or `Owner`.
- The dependency graph is acyclic and every referenced ID exists; walk it to derive waves.
- No task adds scope absent from the spec's goals or lands in a non-goal.
- Task IDs are unique and sequential across milestones.
- The last milestone runs the full verify command and the documentation sync for the plan's documentation-impact rows marked `task`; rows needing separate approval are listed under "Out of tasks (needs approval)".
- Task files exist in the plan's component list or are justified as new.

## Step 7: Write and hand off

1. Write `<feature folder>/tasks.md` from `templates/tasks.md` with `Status: Draft` as the first line and `Overrides: none` unless the user overrode a prerequisite, all boxes unticked.
2. Write `<feature folder>/progress.md` from `templates/progress.md`, empty (sections Completed, Decision, Blocked, Follow-ups, Learnings; each with the placeholder from the template). Never tick a task or add a completion entry: only the executor does that after validation.
3. Use the documentation language and commit-ID conventions found in discovery.
4. Summarize in a few lines: task count, milestones, waves, human-owned tasks, harness gaps, coverage result, counts of coverage rows verified `manual` and `deferred`, env-validation tasks, blocking vs non-blocking human tasks, anything flagged, and plan documentation-impact rows that need separate approval. Ask the human to review and approve; set `Approved` only on their explicit yes. Optionally suggest running the `sdd-doc-reviewer` agent with kind `tasks` and the three paths (`tasks.md`, `spec.md`, `plan.md`) for an independent critique before approval; pass no notes or log file.
5. Only suggest the next command, never run it: `Next: /sdd-executor <feature folder> M1`.

## Guardrails

- No scope absent from the spec; no vague tasks ("refactor", "polish", "finish the feature").
- Never mark tasks done and never touch `spec.md`, `plan.md` or project docs.
- Never invent commands: a missing check is reported and handled by the harness gap rule.
- Do not write implementation code; signatures from the plan are enough.

For a compact worked example of the output, see `references/examples.md` (reference project only; its specifics do not apply elsewhere).
