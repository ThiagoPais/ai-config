---
name: sdd-spec-writer
description: Turn a feature idea, ticket or rough requirement into a reviewed, testable spec.md (problem, goals, non-goals, user stories, Given/When/Then acceptance criteria, edge cases, open questions) by interviewing the user, then save it in the feature's folder. Use this whenever the user says "write a spec", "spec this out", "start a new feature", "define requirements", "what should this feature do", "turn this idea/ticket into acceptance criteria", or wants to update an existing spec.md, even if they never say "spec-driven". This is the first step of the SDD chain; run it before any planning, tasks or coding.
argument-hint: "[idea or ticket id | feature folder]"
---

# SDD spec writer

Turn an idea into a `spec.md` that a human can approve and that later phases (plan, tasks, tests) can build on. A spec decides the **what** and **why**, never the **how**: errors here multiply through every downstream step, so the interview and the self-review are where the value is.

Input: `$ARGUMENTS`

The input is a free-text idea, a ticket reference, or an existing feature folder (which means update mode). If it is empty, ask the user what the feature is. If it is a ticket id and no tracker tool is available, ask the user to paste the ticket text; never guess its content.

## Boundaries

- Write only `spec.md` inside the feature folder. No plan, tasks, code or design content: if the user volunteers implementation detail, park it under Constraints only when it is a real restriction, otherwise note it as input for the plan phase.
- Never set `Status: Approved` yourself. Approval is the human's explicit "yes" in chat; it is what unlocks the next phase. `Status:` is the first line of the file.
- Never overwrite an existing spec; propose a diff (see Update mode).
- Do not touch project docs, instruction files or sibling specs.

## Workflow

### 1. Orient (read-only)

Read `references/discovery.md` and run it: instruction files, specs directory, documentation language, existing templates, commit/ticket conventions. Then skim the project's documentation and a few sibling specs, so your questions are informed and the new spec matches house style. Do not ask the user anything the repository already answers.

Domain documents may be non-text (PDFs, images, datasheets, diagrams). Follow the non-text rule in `discovery.md` and cite page or figure for every fact you take from them. Any environment fact you only inferred (not read) is flagged for the user's confirmation and recorded under Assumptions as `model-proposed`.

### 2. Resolve location

- Compute the feature folder `<specs-dir>/NNN-<slug>/` as described in discovery (highest existing number + 1, zero-padded) and propose the slug from the idea.
- If the input points to an existing folder, or `spec.md` already exists there, switch to **update mode**.
- Confirm folder name and documentation language with the user in the first interview round (fold it into the other questions; do not spend a round on it).

### 3. Interview

Use `AskUserQuestion`. Read `references/question-bank.md` and pick only the questions that apply to this idea; the bank is a menu, not a script.

- At most 4 questions per round, at most 3 rounds. Stop earlier when nothing material is open.
- Put the recommended option first and say why in its description. When the answer is obvious, state it as an assumption inside a question rather than asking blind.
- Round 1: problem, users, scope and non-goals. Round 2: behavior, roles, edge cases and errors. Round 3: constraints, data/integration impact, UI, and anything contradictory from earlier rounds.
- Scope-growth guard: when a question or an answer would add a command, behavior or AC, first ask "in scope or follow-up?" and record follow-ups under Non-goals/Follow-ups. When ACs approach ~15, or the feature hides two features, suggest splitting before drafting more.
- Whatever is still unknown after the last round becomes a `Q#` in the spec. Do not invent an answer to close it. Open questions are strict: plan and tasks refuse to run while any `Q#` is not marked RESOLVED, so push to close them now.

### 4. Draft

Fill `templates/spec.md` (or the project's own template if discovery found one). Write acceptance criteria following `references/ac-writing-guide.md`. Use the project's documentation language.

Put every value the user did not state (model-proposed numbers, defaults, environment facts) under `## Assumptions` as `A#: <assumption> — source: user | model-proposed | environment`. Tag criteria that depend on runtime, transport, host tooling, power, process lifetime or other environment behaviour with `[ENV]` and reference the `A#`: the plan schedules an early validation task for each. Each AC names its observation point.

IDs are stable and unique: `G#`, `NG#`, `US#`, `AC#`, `E#`, `Q#`, `A#`. Later phases reference them, so never renumber an approved spec; append instead. A removed ID stays as a tombstone, `G5: removed (<reason>); ID not reused` (a removed `Q#` adds `-> RESOLVED (<date>)`), so references never silently point at something new.

### 5. Self-review (fix before showing)

Go through this checklist and correct the draft silently; report only what you could not fix.

- Every `AC` is checkable by an automated test or a concrete observation, with a specific expected result, and names its observation point (output line, signal, stored row, response, visible element) reachable through a specified interface.
- Numeric thresholds: state the consequence with a quick calculation (what the number means in time, count or size) and check it against the stated time constants and limits. Numeric bounds must be reachable given those limits; an unreachable bound is a defect.
- Every model-proposed value (and any value the user did not state) is listed under Assumptions and in the hand-over summary for confirmation.
- Criteria that depend on environment behaviour carry `[ENV]` and an `A#`.
- Every `G` and every user story maps to at least one `AC`; every `AC` traces to a goal or story.
- No implementation detail: no technology, class, table, endpoint or file names unless they are an external constraint.
- Non-goals are explicit, so scope cannot creep silently.
- No unmeasured vague words ("fast", "secure", "user-friendly", "easily"): give a number or an observable condition, or move it to `Q#`.
- Edge cases cover the relevant categories from the question bank (empty, concurrent, failure, permissions, limits).
- Re-run this whole self-review after applying any batch of user answers or `Q#` resolutions: answers introduce new numbers and contradictions.
- IDs are unique and consistent; removed IDs are tombstones; each `Q#` is either open (with who can answer) or `RESOLVED (<date>): <answer>`, and the section says `None` when empty.

### 6. Write and hand over

Write `spec.md` with `Status: Draft`. Then reply with a short summary: feature folder, goal count, `AC` count, `E` count, open questions (each one blocks the plan until resolved), and every assumption (the model-proposed `A#` lines) for confirmation. Ask the user to review the file.

This skill does not accept `--light` (only the reviewer and executor skills do); do not offer it. To approve, give the exact replacement for line 1 in the hand-over: `Status: Approved (<user>, <date>)`.

Before accepting an approval, warn the user: if any `Q#` is still unresolved, plan and tasks will refuse to run until each is marked RESOLVED. Set `Approved` only if the user explicitly says yes after that warning. Then set the first line to `Status: Approved (<user>, <date>)`, using the user's name from git config or the instructions file, and today's date. Keep `Approved` only on an explicit user yes. Anything short of an explicit yes ("looks good, but...") means keep Draft and apply the feedback.

End with exactly: `Next: /sdd-plan-writer <feature folder>` (with the real folder path). Only suggest it; never start it.

## Update mode

For an existing `spec.md`:

1. Read it fully, including its status. Read sibling documents (`plan.md`, `tasks.md`) if present, to see what a change would affect.
2. If the user's message already states exact changes, apply them (as in step 3) and show the ID change list afterwards; ask only about the ambiguous remainder. Interview only about the delta.
   - A request for advice ("what do you suggest?") becomes a `Q#` with the recommendation and options, never an AC until accepted.
   - An answer that is itself a new scope item becomes a `Q#` with options (and the in-scope-or-follow-up check), never an AC.
   - An accepted risk (the user overrides a reviewer point) goes to Constraints with owner and date, not as a finding.
3. Show the proposed change as a diff or as an explicit list of added/changed/removed IDs. Do not write the file until the user agrees, except for changes the user already stated exactly.
4. After applying, re-run the self-review, keep existing IDs stable (tombstones for removals), add new IDs at the end, and set the status back to `Draft` if the spec was `Approved`: a changed spec needs a new approval. Resolving a `Q#` follows the same rule.
5. If `plan.md` or `tasks.md` exist, list which of their items may now be stale (by ID) and recommend re-running the downstream skill; do not edit them.

## Quality bar

A good spec is short and exact rather than long. Prefer 5 sharp acceptance criteria over 20 fuzzy ones. If the feature is large, suggest splitting it into several features rather than writing one sprawling spec; a spec that needs more than roughly 15 acceptance criteria usually hides two features.

## Files in this skill

- `references/discovery.md`: shared project-discovery procedure and document conventions. Read in step 1.
- `references/question-bank.md`: framework-neutral interview questions by theme. Read in step 3.
- `references/ac-writing-guide.md`: how to write testable criteria and edge cases. Read in step 4.
- `templates/spec.md`: the output template.
- `references/examples.md`: a worked example from one specific repository; read only if you want to see a filled-in spec, and never copy its project-specific details into other projects.
