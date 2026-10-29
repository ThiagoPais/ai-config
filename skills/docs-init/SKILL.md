---
name: docs-init
description: Scaffold the documentation of a brand-new project in the central docs repo, following CONVENTIONS.md - project folder, overview, PRD stub, roadmap, ADR index, optional DBDD - and wire the code repo back to it (README/CLAUDE.md pointer, .docs-root). Use whenever the user wants to start, create, bootstrap or set up docs or a new project, says "new project", "start documenting X", "create the docs for <name>", "set up the documentation structure", or adds a code repo to a project, even if they don't mention conventions or templates. Works from the docs repo or from a code repo.
---

# docs-init

Creates a new project's documentation so that it is standard-compliant from the first commit. Standard-compliance at birth is cheap; retrofitting is what `docs-migrate` exists for.

## 1. Locate the docs repo and the standard

Run:

```bash
python3 ~/.claude/skills/docs-audit/scripts/docs-lint.py --print-context
```

It resolves the docs repo from (in order) an explicit `--docs-root`, the current directory and its parents (marker file `CONVENTIONS.md`), a `.docs-root` file, `DOCS_ROOT`, and the `docs_root` setting in `docs-audit/config.json`. If it fails, ask the user for the path to the docs repo; never guess.

If the user ran you from a **code repo**, the docs repo is somewhere else: write to it by absolute path. If they ran you from the **docs repo** and the code repo matters (pointer files), ask for its local path.

Then read `<root>/CONVENTIONS.md`, and the templates you will use under `<root>/templates/`. The conventions are the authority; this skill only sequences the work.

## 2. Intake: a brief, or ask once

If the user gives a filled **project brief** (a copy of `<root>/templates/project-brief.md`), read it and take sections 1-3 and 12 as the intake. Ask only for what is blank and required (short name, pitch). Keep the brief's path: `docs-author` and `docs-adr` consume the other sections next. If the user has no brief but wants a rich start, offer the template; otherwise ask as below.

Without a brief, ask once, in one message
Collect only what the scaffold needs, proposing defaults you can infer (the code repo's `package.json`, README, git remote):

- project short name (kebab-case; becomes the folder and file prefix, permanent)
- one-line pitch: what it is and for whom
- code repos: GitHub URLs (and local paths if you will write pointer files)
- stack, if known (leave blank rather than invent)
- does it have a database? (decides whether to create a DBDD stub)
- is there a client proposal to keep? (creates `proposal/`)

Do not interview for requirements here. The PRD interview is `docs-author`'s job and runs next.

## 3. Pre-flight

- The project folder must not exist. If it does, stop and suggest `docs-audit` or `docs-migrate`.
- The name must be kebab-case and not collide with `templates`, `guides`, `tooling`.

## 4. Scaffold

Create, from `<root>/templates/`, substituting `{{project}}`, `{{Project}}`, `{{date}}` (today) and the intake answers:

| File | Status | Notes |
|---|---|---|
| `<p>/<p>.md` | `draft` | Fill summary, repositories, stack from intake. Remove rows in the Documentation map for documents that don't exist yet. Delete all template comments. |
| `<p>/<p>-prd.md` | `draft` | Fill title and overview pitch only. Leave the other required sections as headings with a `TODO` line so the lint shows what is pending. |
| `<p>/<p>-roadmap.md` | `active` | One phase, "Phase 0: documentation", next steps = write PRD. |
| `<p>/adr/README.md` | `active` | From `adr-index.md`, with an empty table (remove the example row). |
| `<p>/<p>-dbdd.md` | `draft` | Only if there is a database. Headings with `TODO`. |

Do not create glossary, ops, features or proposal files until they have content; an empty file is a document that lies about existing. Create `proposal/` only if the user has proposal sources to put there.

Then add the project to the root `README.md` list with its GitHub repos, matching the existing entries' style.

## 5. Wire the code repo (when a local code repo path is known)

Using `<root>/templates/code-repo-pointer.md`:

1. Append the **Documentation** section to the code repo's `README.md` and `CLAUDE.md` (create `CLAUDE.md` if missing). Show the user the exact text and the target files, and write only after they agree: these are files in another repository.
2. Create `.docs-root` there with `root=` and `project=` lines, and add `.docs-root` to its `.gitignore`.
3. Offer the PR-template snippet; do not create `.github/pull_request_template.md` unless asked.

Never commit in the code repo.

## 6. Verify and hand off

1. Run `docs-lint.py <project>`. Expect only `TODO`-driven warnings (missing sections in the PRD). Fix anything else.
2. Report what was created in a short list of paths.
3. Offer the next step (when a brief exists, continue straight into it: `docs-author` PRD from sections 4-9, DBDD from 10, `docs-adr` from 11): `docs-author` in PRD mode to interview the user and fill the PRD, then DBDD, then `docs-adr` for any decisions already made.

Leave git commits to the user unless they ask; if they do, one commit in the docs repo: `docs(<project>): scaffold project documentation`.

## Why these choices

Stubs carry `TODO` headings instead of silence so the lint output doubles as the to-do list. Pointer files are shown before writing because they live in a different repo from the one the user is working in.
