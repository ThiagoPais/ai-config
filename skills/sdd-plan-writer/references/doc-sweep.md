# Documentation sweep procedure

Goal: make sure the plan respects every relevant written decision in the project, and make omissions visible. This runs before codebase exploration because docs tell you what the code is *supposed* to look like.

## 1. Enumerate

Collect candidate files with read-only commands (`find`, `ls`, `git ls-files`), not by guessing. Cover all of:

- Everything under `docs/` and under `doc/`, recursively. Check both even if one is missing; some projects have both, some neither.
- Root-level: `README*`, `ARCHITECTURE*`, `DESIGN*`, `CONTRIBUTING*`, `CHANGELOG*`, `SECURITY*`, `ADR*`, plus instruction files already read in discovery.
- ADR/decision folders anywhere (`adr/`, `decisions/`, `rfc/`, `docs/adr`).
- API and contract definitions: OpenAPI/Swagger (`openapi.*`, `swagger.*`), GraphQL (`*.graphql`, `schema.*`), protobuf (`*.proto`), JSON Schema, database schema/migration docs, security or access rules files when they are documented contracts.
- Diagrams: `.mmd`, `.puml`, `.plantuml`, `.drawio`, `.excalidraw`, other diagram sources.
- Text docs of any folder that is clearly documentation: `.md`, `.mdx`, `.txt`, `.rst`, `.adoc`.
- Binary docs: `.pdf`, images (`.png`, `.jpg`, `.jpeg`, `.svg`, `.gif`), datasheets, schematics, slide decks. Often the authoritative source for limits and pinouts/contracts.
- Sibling spec folders (other `NNN-<slug>/` features and any `_templates/`): for conventions, prior decisions and overlap with this feature.

Exclude dependency and build output (`node_modules`, `vendor`, `dist`, `build`, `.venv`, `target`), lockfiles, and generated files. Say in "Sources consulted" that these were excluded.

Match names case-insensitively (`-iname`; `README.MD`, `Datasheet.PDF` are real). Also list broken symlinks (`find -xtype l`): they are documents you could not read.

Example enumeration (adapt, do not assume these directories exist):

```
find docs doc -type f \( -iname '*.md' -o -iname '*.mdx' -o -iname '*.txt' -o -iname '*.rst' -o -iname '*.adoc' -o -iname '*.mmd' -o -iname '*.puml' -o -iname '*.yaml' -o -iname '*.yml' -o -iname '*.json' -o -iname '*.graphql' -o -iname '*.proto' -o -iname '*.pdf' -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.svg' \) 2>/dev/null
find docs doc -xtype l 2>/dev/null
ls -d README* ARCHITECTURE* CONTRIBUTING* 2>/dev/null
```

## 2. Index

Build a table: path, title (first heading), line count, and the main headings. This is cheap and lets you choose what to read. Keep it in working memory; the final "Sources consulted" list is derived from it.

## 3. Classify and read

For each indexed file decide:

| Class | Criteria | Action |
|-------|----------|--------|
| Relevant | Touches the spec's domain, data, contracts, architecture, security, UX flow, or conventions the plan must follow; or an earlier spec/plan overlapping this feature | Read in full |
| Possibly relevant | Adjacent topics, general guides | Skim headings; read sections that match spec terms |
| Not relevant | Unrelated features, meeting notes, assets | Note as skipped, with the reason |

Search the spec's key nouns (entities, roles, actions) across the whole set (`grep -ril`) to catch relevant files whose titles do not reveal it.

When two documents disagree, do not pick silently. Note the conflict, prefer the one with the more recent/authoritative status if that is clear, and raise it in the plan (as a risk or an open decision for the user).

## 4. Delegate large sets

If the relevant set exceeds roughly 15 files or 3,000 lines, split it into up to 3 groups (by directory or topic) and launch read-only `Explore` subagents in parallel, using the sweep brief in `exploration-prompts.md`. Subagents return per-document summaries plus the constraints that bear on this spec; they do not make design choices. Read the one or two most decisive documents (architecture, data/contract) yourself regardless, because summaries lose nuance. Explore agents read excerpts, not whole files: a document they report only by headings must be re-read by you in the main session if it is relevant to the spec, and is recorded as `headings` only if you did not. Subagents cannot spawn subagents; all delegation happens from you.

## 5. Record

Fill "Sources consulted" in `plan.md`:

- one row per document actually opened (by you or a subagent), with `full`, `headings` or `summary`;
- the versioned/external docs consulted because of instruction-file rules, with version;
- the installed versions of frameworks/boards/libraries the design depends on (lockfile, manifest, package cache) when their APIs differ across majors;
- rows marked `not read` with the reason for broken symlinks, unreadable or undecodable documents, and binary docs you could not open (follow the non-text rule in `discovery.md`; for PDFs and images that were read, cite page or figure);
- "Not consulted (and why)" for relevant-looking files left out.

Never write "no docs found" when binary docs exist: list them. Never list a document you did not open. An honest short list is better than a long inflated one; the reviewer relies on it to find gaps.

## 6. Carry forward

Turn what you learned into plan content: constraints become "Architecture conformance" rows; docs that will go stale go to "Documentation impact"; contracts you must preserve go to "Data models and interfaces"; conflicts go to "Risks". Do not edit the docs themselves.
