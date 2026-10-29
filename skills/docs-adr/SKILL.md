---
name: docs-adr
description: Create, supersede and manage Architectural Decision Records (ADRs) for a project - next number, template, status, immutability rules, two-way supersede links, adr/README.md index - and backfill ADRs from decisions already hidden in existing docs. Use whenever the user mentions ADR, architecture decision, decision record, "we decided to", "why did we choose", "let's record this decision", "we're switching from X to Y", wants to change or revisit a past technical decision, or asks to harvest decisions from the docs, even if they don't say "ADR". Works from the docs repo or a code repo.
---

# docs-adr

ADRs are the project's memory of *why*. The value is in the alternatives and consequences, not the paperwork, so this skill automates numbering and linking and spends the user's attention on content.

## 1. Locate and load

```bash
python3 ~/.claude/skills/docs-audit/scripts/docs-lint.py --print-context
```

Resolve the docs repo and the project (ask if unknown). Read `<root>/CONVENTIONS.md` section 10, `<root>/templates/adr.md`, `<root>/guides/adr.md`, and list the existing `<project>/adr/` files and their frontmatter.

## 2. Pick a mode

| User intent | Mode |
|---|---|
| "record this decision", "we chose X" | **new** |
| "we're replacing X", "revisit decision N", "this no longer holds" | **supersede** |
| "mark N as accepted/rejected/deprecated" | **status** |
| "find the decisions in our docs", "backfill ADRs" | **seed** |
| index out of date | **index** |

## 3. New

1. **Is it worth an ADR?** Apply the test in `guides/adr.md` (hard to reverse, shapes the system, surprising, costs money). If not, say so and where the information should live instead; do not write ADRs for trivia.
2. Number = highest existing number + 1, three digits, never reuse a gap. File `adr/NNN-short-kebab-title.md`.
3. Draft from what the user said and from the project's docs. Ask only for what is missing, in this order of importance: the alternatives that were really considered and why they lost; the downsides; the constraints (cite `FR-xx` where they exist).
4. **Do not invent alternatives or consequences.** If the user cannot name an alternative, write that none was evaluated and mark it `TODO: confirm` rather than fabricating a plausible one. A fake alternative is worse than a gap.
5. Status `proposed` unless the user states it is agreed, then `accepted`. Set `updated` to today.
6. Add it to `adr/README.md` (create the index from `templates/adr-index.md` if missing).
7. Link it from where the decision was stated in prose: replace long explanations in the overview or DBDD with a one-line pointer to the ADR, after showing the user the edit.

## 4. Supersede

1. Read the old ADR fully. Confirm what changes and why the old reasoning no longer holds.
2. Create the new ADR (as in *New*) with `supersedes: NNN`, and in Context explain what changed since the old decision.
3. Edit the old ADR's frontmatter **only**: `status: superseded`, `superseded-by: MMM`. Never touch its body: the history must stay readable and truthful.
4. Update the index. If the new decision changes behavior described elsewhere (DBDD, overview), list those documents for the user and offer to route the update through `docs-author`.

## 5. Status

Allowed transitions: `proposed -> accepted | rejected`, `accepted -> deprecated | superseded`. Anything else, confirm with the user. Change `status` and `updated` only.

## 6. Seed

Scan the overview, PRD, DBDD, roadmap and `CLAUDE.md`/README of the code repo (if available) for choices stated as fact: technology picks, trigger-vs-application rules, hosting layout, auth model, denormalization, vendor selection. Present a numbered candidate list: working title, where it appears (`path:line`), and a one-line reason it deserves an ADR. Let the user choose. Then draft each selected ADR from the existing text, with `TODO: confirm` for anything the docs do not state (typically the alternatives). Create them as `proposed`, in the order the decisions were made if known.

## 7. Verify

Run `docs-lint.py <project>`; fix numbering, index and link findings. Report the ADR path, its status and any documents you recommend updating. Leave commits to the user unless asked (`docs(<project>): add ADR NNN <title>`).

## Why immutability matters

If old ADRs are edited to match the present, nobody can tell what was believed at the time or why things changed. The supersede chain is the audit trail, so the only edits allowed to an accepted ADR are its status and links.
