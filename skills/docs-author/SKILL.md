---
name: docs-author
description: Write or update a project's PRD (product requirements) or DBDD (database design document) by interviewing the user and following the standard templates and guides - requirement IDs, explicit non-goals, ER diagram, invariants - then self-check and lint. Use whenever the user wants to write, draft, fill in, review the content of, update or extend a PRD, product requirements, requirements doc, DBDD, database design, data model doc, ER diagram, or says "document the schema", "add this requirement", "we changed the scope", even if they don't name the document type. Works from the docs repo or a code repo (it reads the schema from the code repo).
---

# docs-author

Interview-driven authoring for the two documents where thinking matters most: the **PRD** (what and why) and the **DBDD** (the data model and its rules). Other document types are mostly derived and are handled by `docs-init` (scaffold, overview, roadmap) and `docs-adr` (decisions).

## 1. Locate and load

```bash
python3 ~/.claude/skills/docs-audit/scripts/docs-lint.py --print-context
```

Resolves the docs repo and, when run from a code repo with a `.docs-root`, the project. If it fails or the project is unknown, ask. Then read:

- `<root>/CONVENTIONS.md` (sections 5-8)
- `<root>/templates/<prd|dbdd>.md` and `<root>/guides/<prd|dbdd>.md`
- the project's existing document, if any, plus its overview, PRD (for DBDD mode), roadmap, ADR index

If the user supplied a filled project brief (`templates/project-brief.md`), read it too: sections 4-9 prefill the PRD and section 10 the DBDD. Draft from it first, then interview only on gaps, vague wording and thin non-goals; confirm drafted answers with yes/no rather than re-asking.

Decide the mode: **create** (no document yet, or only TODO stubs) or **update** (existing content; apply a change). In update mode, read the whole document first and change only what the request touches.

## 2. PRD mode

Follow `guides/prd.md`. Interview in short rounds of two to four questions, in this order, skipping what the existing docs already answer (propose an answer from them and ask for a yes/no instead of an open question):

1. Problem and users: who has the problem, what happens today.
2. Goals and success: what outcome, how will they know.
3. Requirements: capture as one-line verifiable statements; assign `FR-nn`/`NFR-nn`, priority and phase as you go.
4. Boundaries: what must the product *not* do. Keep pushing for at least one real non-goal; clients rarely volunteer them.
5. Constraints, assumptions, open questions with owners.

Rules that keep the PRD useful:

- **Business language only.** When the user volunteers technology ("with NestJS", "a CRON job"), keep the need in the PRD and route the technology: stack goes to the overview, a firm choice to `docs-adr`. Tell the user you moved it and why.
- **IDs are permanent.** Continue numbering from the highest existing ID. Never renumber; a dropped requirement stays as `(removed)` with a reason.
- **Make it testable.** Rewrite "fast" as a measure, or record it as an open question.
- When the scope change affects phases, update the roadmap's requirement references, or tell the user to.

## 3. DBDD mode

Follow `guides/dbdd.md`. The schema file in the code repo is the source of truth for columns; the DBDD explains what it cannot.

1. Find the schema. From a code repo it is the cwd; from the docs repo ask for the code repo's local path. Look for `prisma/schema.prisma`, SQL migrations, or ORM entities. If there is no schema yet, work from the PRD and mark the document `draft`.
2. Generate the ER diagram (Mermaid) from the schema or, without one, from the PRD's nouns. Show keys and relationships; omit types unless they carry meaning.
3. Interview only for what the schema does not say: for each entity its purpose and non-obvious fields; for each rule *what must always hold, why, and where it is enforced* (constraint, trigger, application); lifecycle and retention; the reason for each index.
4. For every rule or structure that looks like a decision (denormalized counter, trigger-based lock, single storage bucket), ask whether it deserves an ADR and hand the list to `docs-adr` instead of explaining the *why* at length inside the DBDD.
5. State the schema file location in the Overview section, and never paste column tables that duplicate it.

## 4. Self-check, write, verify

1. Compare the draft against the guide's checklist and fix misses before showing it. Report any checklist item you could not satisfy and why.
2. Write the document with frontmatter (`status: draft` until the user says active; `updated` = today). Keep required `##` headings from the template; delete template comments.
3. Run `docs-lint.py <project>` and resolve findings on the files you touched.
4. Summarize in a few lines: what changed, IDs added or removed, content you re-routed, open questions left. Suggest `docs-audit` for an independent review and `docs-adr` for decisions you identified.

## Principles

Questions are cheap for the user and wrong assumptions are expensive for the project, so ask in small rounds and propose defaults. Never invent a requirement, constraint or measure; record unknowns as open questions with an owner.
