# Review brief (template passed to `sdd-doc-reviewer`)

Fill the placeholders and send this as the whole prompt. Paths only; no summaries, no author reasoning, no opinion on quality.

```
You are reviewing a document you did not write. Be adversarial: fail by default.

Kind: <spec | plan | tasks>
Rigor: <standard | light>
Document: <path>
Upstream documents: <paths, or "none", or "<name> is missing">
Project documentation index (read what is relevant, grep the rest): <paths: instruction files, docs/, doc/, ADRs, architecture and data/contract docs>

Instructions:
- Apply the checklist for this kind exactly as in your definition, then the kind-specific focus below.
- Cite a location (section, ID or line) for every finding. For contradictions cite both sources as path:line.
- Confirm referenced paths, modules and symbols exist with Grep/Glob; do not assume.
- Do not edit anything. Propose the minimal exact change per finding.
- Open only the paths listed here and files they reference; never progress.md, notes, logs or files found only by listing the repo. If you must, say so.
- List every document you opened under "Files reviewed". Tag claims from your own knowledge as "(own knowledge, unverified)". For non-text evidence cite page/figure.
- An acceptance criterion that cannot be tested as written (no observation point, undefined token/interface, unreachable bound) is a blocker.
- Output: VERDICT, Files reviewed, numbered findings with severity (blocker | major | minor), location, problem, evidence, suggested change; then "Questions for the human" (merged with overlapping findings, safe defaults marked "non-blocking (default: X)"); end with "Remaining: <n> blockers, <m> majors, <k> minors — approve now?".
- If Rigor is light: report only blockers and majors, and give minors as "known minors: N".
```

## Kind-specific focus

### spec
- Every `AC` is observable and testable; flag unmeasured words ("fast", "secure", "simple", "intuitive", "properly") and criteria that cannot fail.
- Every `G` and user story maps to at least one `AC`; every `AC` traces to a goal.
- Implementation leaked in (technology, file, class, library choices) where only behaviour belongs.
- Non-goals explicit; edge cases cover empty, invalid, unauthorised, concurrent, offline/failure and boundary conditions relevant here.
- Open questions: every `Q#` RESOLVED, or the section says `None`; flag assumptions that are really unasked questions.
- Tombstone integrity: removed IDs are listed with a reason and never reused.
- Contradictions inside the spec or with project docs; first line is a valid Status line.

### plan
- Every `AC` and `E` of the spec appears in the Traceability section with a test level that can actually prove it; each env-validation row states "if it fails: reopen the spec".
- Every listed path exists or is marked new; reused modules and symbols really exist.
- Decisions state rationale and rejected alternatives; none contradicts the spec or the project's architecture and layering rules (cite them).
- Scope: nothing beyond the spec's goals; no tasks or implementation code.
- Risks have mitigations; the documentation-impact section and "Sources consulted" list are plausible, and project docs that look relevant but are missing from it are flagged.

### tasks
- Every `AC` and `E` is covered by at least one task; the coverage matrix is correct, not just present.
- Each task has `Covers`, `Depends on`, `Files`, `Done when` (a runnable command plus an observable condition), `Parallel`, `Owner`.
- Tasks are one session each (about five files or fewer) and leave the project passing.
- Dependency graph acyclic; referenced IDs exist; `Parallel: yes` tasks share no file in the same wave.
- Human-owned work and manual-only checks are marked `Owner: human`; tasks with no automated test say `Tests: none (<reason>)` with reason in `docs-only | infrastructure | hardware-glue | manual`.
- A "Deferred / unverified" section is present and the coverage matrix `Verified by` values are valid (`auto | manual | deferred`).
- Milestones end with a checkpoint; test-harness gaps have an early task; no task adds scope absent from the spec or from the plan's files.

## Stricter pass (use once, only after a suspicious PASS)

Append this to the brief:

```
A previous pass reported no findings on this document. That is unlikely for a document of this size. Do not argue for the document: for each checklist item, quote the exact text that proves it satisfied, and list at least one thing a careless approver would miss (even if minor). Check each AC/E/task by ID, one by one. Report any item for which you cannot quote proof.
```

If the second pass still finds nothing blocking after quoting proof per item, accept PASS and state that it was re-briefed.
