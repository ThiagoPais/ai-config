# Task sizing and slicing

Read this when a task feels too big, too thin, or when the grouping into milestones is unclear.

## Right size
A task is right-sized when all of these hold:
- One focused session; a fresh context can finish it from spec + plan + the task alone.
- One commit, with a message the history can use as a changelog line.
- About 5 files or fewer (source plus tests). More than that usually hides two outcomes.
- A single concrete "Done when" with a command that exits non-zero on failure.
- The project passes its verify command afterwards, so a failed later task never strands a broken tree.

## Too big, split when
- The title needs "and" to describe it.
- It spans more than one layer without a reason (data plus logic plus interface).
- Its "Done when" has several unrelated conditions.
- It covers more than ~3 acceptance criteria that do not share code.
- You cannot say what the failing test would look like.

## Too small, merge when
- The task cannot be verified on its own (a type declaration with no consumer, a file move).
- It would produce a commit nobody would review separately.
- It always changes together with a neighbour that it blocks.

## Slicing patterns (vertical, not horizontal)
- **Walking skeleton first:** the thinnest end-to-end path (one input to one visible result) before breadth.
- **By acceptance criterion:** one task per AC (or small group) when ACs are independent.
- **By edge case:** happy path first; each edge case or error path as its own follow-up task unless it shares all code with the happy path.
- **Contract before consumers:** when several tasks use a type, schema or interface, the contract task comes first and its dependants can be parallel.
- **Seams for parallelism:** split along module or file boundaries so same-wave tasks do not share files.
- **Harness first:** if a layer has no runnable check, the task that creates it precedes everything that depends on it.
- **Human steps isolated:** put each manual or shared-environment action in its own `Owner: human` task, so agent tasks never block mid-way. Mark `Blocking: no` when independent agent work can continue; list it as deferred in the final milestone.
- **Env validation first:** one `Type: env-validation` task per environment-assumption row, in the first milestone, before logic that depends on it.

## "Done when" patterns
- Behavior: `<test command> <test path>` passes, and <the new test names exist and ran>.
- Contract/schema: `<typecheck or contract check>` passes, and <the artifact lists the new field/endpoint>.
- Interface: `<test or build command>` passes, and <the state/screen/response described in the AC is reproducible with these steps>.
- Docs: <document X contains section Y reflecting decision D#>; `<doc lint/link check if the project has one>` passes.
- Manual: `manual`: <numbered steps and the exact expected observation>, or the name of the plan's manual verification procedure. Use only under the harness gap rule, `hardware-glue`, or a `Type: env-validation` task that covers an AC (`Tests: none (manual)`).

Weak forms to rewrite: "works as expected", "tests pass" without naming which, "code reviewed", "refactored".

## Waves worked example
Waves are computed within a milestone: the executor stops at every milestone checkpoint, so tasks in different milestones never run together. A dependency on an earlier milestone counts as satisfied. Group the waves table by milestone.

Tasks of one milestone: T1 (none), T2 (none), T3 (T1), T4 (T1, T2), T5 (T3, T4).
- Wave 1: T1, T2. Wave 2: T3, T4. Wave 3: T5.
- If T3 and T4 both list `src/x`, they overlap: both are `Parallel: no` and run sequentially in ID order. A same-wave task that overlaps nothing stays `yes`.
- T5 is alone in its wave: `Parallel: no`.

## Milestone sizing
3 to 6 tasks each, ending in something a human can see or run. If a milestone only contains infrastructure, say so in its name; the human then knows there is little to look at.
