---
name: sdd-plan-writer
description: Turn an approved spec.md into a grounded plan.md (the "how"): architecture decisions, files touched, risks, testing strategy and an AC-to-test Traceability section, based on the real codebase AND all of the project's documentation. Use whenever the user says "plan this spec", "create the plan for this feature", "design how to build this", "write plan.md", "technical design for the spec", or runs /sdd-plan-writer, even if they never mention SDD. Refuses to run unless spec.md is Approved and all questions are resolved. Produces a Draft plan for human review and suggests /sdd-task-writer next.
argument-hint: "[feature folder]"
---

# SDD Plan Writer

Produce `plan.md` for a feature: the *how*, derived from an approved `spec.md` and grounded in what the project really contains (code and documentation). The plan is the highest-leverage review checkpoint in spec-driven development: a wrong design gets implemented faithfully, task after task. So the plan must be evidence-based, traceable to the spec, and honest about what it did and did not read.

Feature folder (from the invocation): `$ARGUMENTS`

If `$ARGUMENTS` is empty, run discovery, list the feature folders in the specs directory that have an Approved `spec.md` and no `plan.md`, and ask which one to plan (recommended option first).

## Guardrails

- Never edit `spec.md` or any project documentation. If the spec is wrong or ambiguous, or a doc needs changing, propose the exact change in chat and stop or continue as the user decides. Upstream documents are the human's; drift stays a conscious decision.
- Never mark the plan `Approved`. Write `Status: Draft`; only the user's explicit yes changes it.
- Editing an Approved plan (update mode) resets it to `Status: Draft`; a changed plan needs a new approval.
- No scope beyond the spec's goals. Ideas outside scope go to a "Follow-ups" note in the summary, not into the design.
- No tasks and no implementation code in the plan: signatures, type shapes and contracts only. Tasks belong to the next skill.
- Read-only everywhere except writing `plan.md` in the feature folder.

## Step 0 - Discovery and prerequisites

1. Run the shared procedure in `references/discovery.md` (instruction files, specs directory, stack, verify commands, test conventions, commit convention, doc language, templates). Keep the results; you need them in Steps 1, 2 and 4.
2. Resolve the feature folder from `$ARGUMENTS` (path, folder name, or `NNN` prefix).
3. Check the hard prerequisites on `<feature folder>/spec.md`:
   - the file exists;
   - its first line is `Status: Approved (...)` (a missing Status line counts as Draft);
   - the "Open questions" section has no `Q#` that is not marked RESOLVED (`None` is fine).
4. If any check fails, **stop**. List each blocker precisely (file, line, the offending `Q#` or status) and tell the user what to do (typically: finish the spec with `/sdd-spec-writer`, resolve the questions, approve). Continue only if the user explicitly overrides in chat; if they do, record the override and the open items under "Assumptions" in the plan.
5. If `plan.md` already exists, do not overwrite: switch to update mode, read it, and propose a diff for the user's approval. After applying, set `Status: Draft` if it was Approved, and list which `tasks.md` items may now be stale (by ID) so the user re-runs `/sdd-task-writer`; do not edit `tasks.md`.
6. Read `spec.md` completely and list its `G`, `NG`, `AC`, `E` and constraints. These are the contract the plan is checked against.

## Step 1 - Documentation sweep (mandatory)

The plan must respect decisions already recorded in the project's documents, including ones the spec author never thought of. A design built from code alone repeats past mistakes and contradicts written architecture. Follow `references/doc-sweep.md` for the exact procedure; in short:

1. **Enumerate** every documentation file under `docs/` **and** `doc/` (recursively), plus root-level docs (`README*`, `ARCHITECTURE*`, `CONTRIBUTING*`, `CHANGELOG*`), ADR folders, API schemas (OpenAPI/Swagger, GraphQL, protobuf, JSON Schema), diagrams (`.mmd`, `.puml`, `.drawio`), and any `.md`, `.mdx`, `.txt`, `.rst`, `.adoc`. Match extensions **case-insensitively** and include `.pdf`, images and datasheets: binary docs often hold the hardest constraints. Include sibling spec folders for conventions and prior decisions.
2. **Index first**: path plus title/headings for each file. Cheap, and it shows the whole landscape.
3. **Read in full** every document relevant to the spec's domain (architecture, data/contract docs, UX/design docs, security, previous specs touching the same area). **Skim by headings** the rest.
4. **Delegate** when the set is large (more than ~15 files or ~3,000 lines): up to 3 read-only `Explore` subagents in parallel, partitioned by directory or topic, each returning per-document summaries with the constraints that matter for this spec. The briefs are in `references/exploration-prompts.md`. Explore agents read excerpts, so a document they report only by headings must be re-read by you if it is relevant to the spec.
5. **Record** every consulted document in the plan's "Sources consulted" section with how it was read (full / headings / skipped and why). The reviewer uses this list to spot omissions, so be exact, and never list a file you did not open.
6. **Unread is listed, never hidden**: broken symlinks and documents you cannot read (binary, unreadable, too large) go in "Sources consulted" as `not read` with the reason. Follow the non-text rule in `references/discovery.md`, and cite the page or figure for anything you did read from a PDF or image.

If neither `docs/` nor `doc/` exists, say so in "Sources consulted" and rely on root-level docs and instruction files. Never write "no docs found" when binary docs (PDF, images, datasheets) exist.

## Step 2 - Codebase exploration (read-only)

Ground the design in the code that exists: modules the feature touches, patterns to follow, utilities to reuse, test setup, integration points. Delegate to `Explore` subagents (parallel when the questions are independent, at most 3), using the briefs in `references/exploration-prompts.md`. Give each a narrow question and ask for paths with line references, not file dumps. Verify the claims that your design will depend on by opening the key files yourself; subagent summaries are leads, not proof.

Before designing around any framework, library or platform API, follow the project's own rules for that (for example "fetch the versioned docs for the installed major version before using X" in the instruction files). Read the installed version from the manifest, consult the matching documentation the project points to, and cite it in "Sources consulted". Do not design from memory against APIs that change between releases.

Also check the **installed versions** of the frameworks, libraries and boards/targets the design depends on (lockfile, manifest, package cache, SDK/toolchain version) whenever their APIs differ across major versions, even if no project rule asks for it. Record each version and the doc consulted in "Sources consulted". Why: a design that is valid for another major version fails only at implementation time.

## Step 3 - Design

1. For each significant choice, write a decision `D#`: the decision, the rationale (tie it to a `G`, `AC`, `E` or constraint, or to a project doc), and the alternatives considered (not chosen) with a one-line reason each. Use the template's per-D# structure (`Decision` / `Why` / `Alternatives considered (not chosen)`).
1a. **Pin every observable.** Each format, identifier, interface or accessor that a test will assert (message shape, field names, exit codes, file names, units, ordering, accessor signatures) must be decided in the plan, in an interface/format entry or a D#. Why: the test-writer cannot invent it and an unpinned observable lets test and implementation diverge. If it cannot be decided from the spec, docs or code, it returns to the spec: stop, propose the exact new `Q#` (text and options) and wait; do not guess.
1b. **Environment assumptions.** For every spec `[ENV]` criterion and every `Assumptions` entry (`A#`), decide how and when it is validated on the real target, and which early task validates it. Carry these into the plan's "Environment assumptions validation" section.
2. Ask the user only about decisions that are genuinely open and consequential (`AskUserQuestion`, at most 4 per round, recommended option first, with the trade-off in the option text). Decide the rest yourself and say why in the plan. Never ask what the repository or docs already answer.
3. Check the design against the architecture and layering rules found in the instructions and docs; this becomes "Architecture conformance". If a rule conflicts with the spec, surface it as a blocker rather than silently choosing.
4. Prefer the smallest design that satisfies the spec. Reuse existing patterns over inventing new ones; name any new dependency and the project's own convention for installing it.
5. Optional challenge: when the feature is large, risky or touches shared contracts, hand the draft to the global `sdd-doc-reviewer` agent (kind `plan`, plan path, spec path, the project doc paths that matter) before presenting. Never pass your own notes or any log file path: the reviewer must judge the document, not your reasoning. Treat its findings as input, fix what is valid, and mention in the summary that it ran. It is read-only and cannot spawn further agents. For a small, low-risk feature it is optional.

## Step 4 - Write plan.md

Use the project's template if one exists in `<specs-dir>/_templates/`; otherwise use `templates/plan.md`. Write to `<feature folder>/plan.md` in the language of the existing project docs (default English). Keep it precise rather than exhaustive: a reader should be able to judge the design in one sitting.

Required sections (the template carries the layout): Approach summary, Sources consulted, Architecture decisions, Architecture conformance, Components / files touched, Data models and interfaces, Documentation impact, Risks and mitigations, Testing strategy, Verify commands, Traceability, Rollout / migration notes, Assumptions (only if any).

Include these only when relevant (omit otherwise, do not write "n/a"):
- **Environment assumptions validation**: one row per spec `[ENV]` criterion/assumption: the assumption, how and when it is validated on the real target, the early validation task (the task writer schedules it FIRST, `Type: env-validation`), and "if it fails: reopen spec".
- **Bring-up and safe first run**: order of power-on/enablement, how to limit damage if something is wrong, what a healthy first output looks like, environment prerequisites the README must state.
- **Manual verification procedures**: a step list for each `manual` row of the Traceability section.

Rules for the content:
- Every path in "Components / files touched" either exists (you opened or listed it) or is marked `new`.
- The Traceability section has one row per `AC#` and `E#` from the spec: component(s) that satisfy it, and a test level from `unit | integration | e2e | contract | manual`. Pick the lowest level that can genuinely prove the criterion; a `manual` row needs a procedure (steps in "Manual verification procedures"). The optional "Also" column records a secondary level (for example `unit + manual`) when one level cannot cover the criterion alone. Criteria marked `[ENV]` must not be proven only by tests on a substitute host: map them to a level that runs on the real target, or add an "Also" entry that does.
- "Verify commands" lists only commands confirmed to exist in discovery, labelled test / lint / typecheck / build / verify-all. If a layer has no runnable check, say so; the task writer will plan a harness task. A command the plan itself introduces (a new harness, script or target) is recorded as a decision D# and listed as `unconfirmed (created by T#)`; this is allowed and does not violate "never invent commands", because it is declared, not assumed. Test-level rows whose only possible check is not automatable use `Tests: none (<reason>)` downstream, with the reason from docs-only | infrastructure | hardware-glue | manual.
- "Documentation impact" lists existing docs that must change (architecture, data model, API/contract, README, ADR), what changes, and whether it is applied by a task or needs separate approval. You do not edit them.
- No time estimates, no task breakdown, no code bodies.

## Step 5 - Self-review (fix before showing)

Run this checklist against the written file and repair any failure:

- [ ] Every `AC` and `E` from the spec appears in the Traceability section with a valid test level.
- [ ] Every `G` is served by at least one decision or component; nothing in the plan lacks a spec goal behind it.
- [ ] Every path exists or is marked `new`.
- [ ] No contradiction with `spec.md` or with any document in "Sources consulted" (re-check the architecture and data docs specifically).
- [ ] Every decision has `Why` and alternatives considered (not chosen).
- [ ] Every observable a test will assert (format, identifier, interface, accessor) is pinned in the plan, or returned to the spec as a proposed `Q#`.
- [ ] Every `[ENV]` criterion has a row in "Environment assumptions validation" with a validating early task.
- [ ] Every spec Assumption `A#` is carried into the plan or explicitly flagged (with `source`) for the user.
- [ ] Any command introduced by the plan is a D# and marked `unconfirmed (created by T#)`.
- [ ] Every risk has a mitigation.
- [ ] New dependencies are named with the project's installation convention.
- [ ] "Sources consulted" is complete and truthful; versioned docs and installed versions are cited; unread docs (binary, unreadable, broken symlinks) are marked `not read` with a reason.
- [ ] "Documentation impact" and "Verify commands" are filled in (or explicitly "none").
- [ ] No tasks, no implementation code, no scope beyond the spec.
- [ ] `Status: Draft` is the first line of the file.
- [ ] Every path in the "Sources consulted" table was opened by you or reported in full by a subagent.

## Step 6 - Summary and gate

Reply with a short summary: the approach in 2 to 3 sentences, number of decisions and risks, the AC/E coverage by test level, documents consulted count (and how many were delegated), documentation that needs updating, any decision the user should look at first, and whether `sdd-doc-reviewer` was used (optional for a small, low-risk feature). Ask for review of `plan.md`. Do not set `Approved` yourself; when the user approves, they (or you, on their explicit yes) change the Status line.

End with exactly one hand-off line and do not start the next phase:

`Next: /sdd-task-writer <feature folder>`
