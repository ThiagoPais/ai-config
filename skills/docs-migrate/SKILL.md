---
name: docs-migrate
description: Bring an existing or legacy project's documentation up to CONVENTIONS.md - classify every file, produce a reviewable move/split/rename/trim plan, then apply it with git mv, frontmatter stamping, link repair and a before/after lint, without losing content. Use whenever the user wants to reorganize, restructure, standardize, clean up, migrate, refactor or "put in order" project documentation, fix audit findings about layout or naming or structure, split an overloaded overview into overview + roadmap, or apply the new documentation standard to an older project, even if they don't say "migrate". Works from the docs repo or a code repo.
---

# docs-migrate

Retrofits a project to the standard in three phases with a human gate between planning and applying. Reorganizing documents is easy to get subtly wrong (a section silently dropped, a link left dangling), so the plan is explicit, content is only ever moved, and the result is verified.

## 1. Locate and baseline

```bash
python3 ~/.claude/skills/docs-audit/scripts/docs-lint.py --print-context
```

Resolve the docs repo and the project (ask if unclear). Read `<root>/CONVENTIONS.md` (all of it: sections 2, 5, 6, 8 drive decisions) and the templates. Require a clean git working tree for the project folder; if it is dirty, ask the user to commit or stash first, so the migration is isolated and reversible.

Capture the baseline: `docs-lint.py --json <project>` and keep the counts.

## 2. Phase 1: Inventory (read-only)

For every file under the project folder produce a row: current path, detected type (overview, prd, dbdd, adr, roadmap, glossary, ops, proposal source, asset, CI/script, build artifact, unknown), and its H2 sections with a destination per section using CONVENTIONS section 8 (who owns which fact).

Common legacy patterns and where they go:

| Found | Destination |
|---|---|
| Progress log, status, "next steps" in the overview | `<p>-roadmap.md` (Log / Next steps / Current phase) |
| Tech stack, data flow, architecture inside the PRD | Overview (Stack/Architecture); firm choices become ADR candidates |
| Auth/security blueprint inside the overview | ADR candidates (decisions) + feature spec (behavior); keep one summary line in the overview |
| Standalone `ER-Diagram.md` | `<p>-dbdd.md`, Entity-relationship diagram |
| Numbered headings (`## 3. Schema`) | Same section, number removed |
| CI workflows / setup scripts at the project root | `infra/` (live copies belong to the code repo) |
| `<p>_proposal/` or `<p>-proposal/` | `proposal/` (sources + final PDF only) |
| `.aux .log .fls .fdb_latexmk .synctex.gz` | Untrack and git-ignore |
| Credentials/passwords in any file | **Do not copy or move them.** Flag to the user for removal and rotation |

## 3. Phase 2: Plan (still read-only)

Write the plan to the conversation (and to `<project>/MIGRATION-PLAN.md` only if the user asks), as ordered steps:

1. **Renames/moves** (`git mv old -> new`).
2. **Splits** (section X of file A -> section Y of file B), naming every section.
3. **Rewrites** limited to: stamping frontmatter, removing heading numbers, fixing links, removing template comments. No prose edits.
4. **Removals**: only build artifacts (untrack) and nothing else.
5. **Left for a human**: items you could not classify, decisions to turn into ADRs (list titles; `docs-adr` seed mode does the work), requirement IDs missing from the PRD (`docs-author`), missing required sections.
6. **Accounting**: a table showing every original H2 section -> `kept` / `moved to <path>#<section>` / `unclassified`. No section may be unaccounted for. Nothing is deleted without an explicit user line "drop X".

Ask the user to approve or edit the plan, and ask whether to commit after each step (default: one commit per step, message `docs(<project>): <step>`). **Do not apply anything before approval.**

## 4. Phase 3: Apply

Execute step by step, in this order so that links are repaired once at the end:

1. `git mv` renames and folder moves.
2. Splits: create the destination from its template, move the text verbatim under the right heading, leave a one-line pointer where the content used to be if the source document keeps a reason to mention it.
3. Stamp frontmatter on every standard document: `type`, `project`, `status` (`draft` unless the document is clearly in use, then `active`), `updated` today.
4. Strip heading numbers; keep section order unless the template order is clearly better and the plan said so.
5. Repair relative links: grep the project (and the root `README.md`) for old paths and update them. Update the root README project entry if the folder layout it describes changed.
6. Untrack build artifacts (`git rm --cached`) and propose `.gitignore` lines.

Never change wording inside moved content. If a moved block breaks the owning document's flow, leave a `TODO` for the user rather than rewriting it.

## 5. Verify and report

1. Run `docs-lint.py <project>`; show baseline vs. now (errors/warnings/info).
2. Re-run the accounting: confirm every original section exists at its new location (grep a distinctive line from each moved section). Report any mismatch as a failed migration step, not as a footnote.
3. Hand over the remaining work as a short list mapped to skills: `docs-adr` (decisions), `docs-author` (PRD IDs, missing sections), `docs-audit` (independent review).

The migration is idempotent: running it on a compliant project produces an empty plan, which is the signal that it is done.
