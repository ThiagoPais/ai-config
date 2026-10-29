Status: Draft

# Spec: <feature name>

Feature folder: <specs-dir>/NNN-<slug>/
Source: <ticket id, link or "idea from <user>, <date>">

ID convention: a removed ID stays as a tombstone, e.g. `G5: removed (<reason>); ID not reused`; for a question, `Q3: removed (<reason>); ID not reused -> RESOLVED (<date>)`.

## Problem

<Who has what problem, and why it matters now. 3-6 sentences. No solution.>

## Goals

- G1: <outcome the feature must achieve>
- G2: ...

## Non-goals

- NG1: <explicitly out of scope, and why if not obvious>

## User stories

- US1: As a <role>, I want <capability>, so that <benefit>. (serves G1)
- US2: ...

## Acceptance criteria

Each criterion is a testable statement with a concrete observable result.

Each criterion names its observation point (output line, signal, stored row, API response, UI element). Criteria that depend on runtime, transport, host tooling, power, process lifetime or other environment behaviour carry `[ENV]` and reference an `A#`; the plan schedules an early validation task for each.

- AC1: Given <context>, when <action>, then <observable result at <observation point>>. (G1, US1)
- AC2 [ENV]: Given ..., when ..., then ... (G2, US2; A1)

## Assumptions

Every model-proposed value and every value the user did not state. Listed in the hand-over for confirmation. Write `None` when empty.

- A1: <assumption> — source: user | model-proposed | environment

## Edge cases and error handling

- E1: <input or condition> -> <expected behavior>
- E2: ...

## Constraints

Only real restrictions, each measurable or checkable. Remove the lines that do not apply.

- Performance: <number + condition>
- Security / privacy / compliance: <rule>
- Compatibility / platforms: <list>
- Other: <deadline, cost, legal, dependency on another team>

## Documentation impact (flags only)

Existing project documents this feature appears to change (architecture, data model, API/contract, README). Flag only; the design belongs to the plan phase.

- <document path or kind> -> <what will likely need updating>

## Open questions

Write `None` when there are no questions (no placeholder Q1).

- Q1: <question> - <who can answer>
- Q2: <question> -> RESOLVED (<date>): <answer>

> Every Q# must be marked RESOLVED before the plan and tasks phases proceed.
