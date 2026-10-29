Status: Draft

# Tasks: <feature name>

Source: spec.md (Status: Approved (<user>, <date>)), plan.md (Status: Approved (<user>, <date>))
Overrides: none <or the prerequisite the user explicitly overrode, with the date>

Legend: [ ] todo, [x] done. Only the executor ticks boxes, after validation.
Metadata: `Parallel: yes|no` (safe to run alongside other tasks of the same wave), `Owner: agent|human` (human also when the only check is `manual`), `Blocking: yes|no` (human tasks only: `no` lets later independent agent tasks proceed), `Type: env-validation` (optional; failure reopens the spec).
Tests: every task that covers an AC/E has its test files in `Files`; otherwise `Tests: none (<reason>)` with reason in docs-only | infrastructure | hardware-glue | manual. `hardware-glue` on an AC task needs a one-line justification and a `manual` Done-when pointing at the plan's manual procedure.
Verify commands: `<test>`, `<lint>`, `<typecheck>`, `<verify all>` (from plan.md / discovery)

## Execution waves

Waves are computed within a milestone (the executor stops at every checkpoint).

| Milestone | Wave | Tasks | Notes |
| --- | --- | --- | --- |
| M1 | 1 | T1, T2 | T1 and T2 are independent and share no files |
| M1 | 2 | T3 | depends on T1 |
| M2 | 1 | T4 | earlier-milestone dependencies count as satisfied |

## Milestone 1 (M1): <name>

- [ ] **T1: Validate <environment assumption A1>**
  - Type: env-validation
  - Covers: A1, AC1 [ENV]
  - Depends on: none
  - Files: none
  - Tests: none (manual)
  - Done when: <the plan row's observation>. If it fails: stop, propose the exact spec change (reopens the spec).
  - Parallel: yes
  - Owner: human
  - Blocking: yes

- [ ] **T2: <short imperative title>**
  - Covers: AC1, E1
  - Depends on: none
  - Files: `path/to/file` (new), `path/to/test`
  - Done when: `<test command> <path>` passes, and <observable condition>
  - Parallel: yes
  - Owner: agent

- [ ] **T3: <hardware-bound glue>**
  - Covers: AC2
  - Depends on: T2
  - Files: `path/to/glue`
  - Tests: none (hardware-glue): <one-line why automation is impossible>
  - Done when: manual procedure "<name>" from plan.md "Manual verification procedures" shows <observation>
  - Parallel: no
  - Owner: human
  - Blocking: no

- [ ] **T4: <short imperative title>**
  - Covers: AC3
  - Depends on: T2
  - Files: ...
  - Done when: `<command>` passes, and <observable condition>
  - Parallel: no
  - Owner: agent

> MILESTONE CHECKPOINT: stop and report to the human.

## Milestone 2 (M2): <name>

...

> MILESTONE CHECKPOINT: stop and report to the human.

## Milestone N (MN): Validation and documentation sync

- [ ] **Tn: Run full verification**
  - Covers: every AC/E (verification only)
  - Depends on: <all previous tasks>
  - Files: none
  - Tests: none (infrastructure)
  - Done when: `<verify all command>` passes, and every AC/E in the matrix below has a passing check or a documented manual check; every `deferred` row is listed under "Deferred / unverified" below
  - Parallel: no
  - Owner: agent

- [ ] **Tn+1: Sync documentation**
  - Covers: plan.md "Documentation impact" rows marked `task`
  - Tests: none (docs-only)
  - Depends on: Tn
  - Files: <docs from plan documentation-impact rows marked `task`>
  - Done when: each listed document reflects the implemented behavior, and the diff touches only those documents
  - Parallel: no
  - Owner: agent

> MILESTONE CHECKPOINT: stop and report to the human.

## Deferred / unverified

Human rows still pending (`Blocking: no`). The feature is not "done" until each is verified. Write `None` if there are none.

- <T# title> -> <AC/E it verifies, procedure name>

## Out of tasks (needs approval)

Plan documentation-impact rows marked `needs separate approval`. Never tasks; the human decides. Write `None` if there are none.

- <document path> -> <required change>

## Coverage matrix

| ID | Description (short) | Tasks | Verified by |
| --- | --- | --- | --- |
| AC1 | ... | T1, T4 | auto |
| AC2 | ... | T3 | deferred |
| E1 | ... | T1 | manual |
