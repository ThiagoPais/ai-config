---
name: sdd-init
description: One-time bootstrap of Spec-Driven Development in a repository: discovers the specs directory, verify/test/lint/typecheck/build commands, test-file patterns, commit convention and documentation language, then (after your approval) adds a short `SDD` section to the project's instruction file and creates the specs directory. Explicit invocation only - run it as /sdd-init [specs dir] once per repository, before the first /sdd-spec-writer.
disable-model-invocation: true
argument-hint: "[optional: specs dir]"
---

# sdd-init

Make SDD discovery deterministic in a repository: record the project's SDD settings once, in a short `## SDD` section of its instruction file, so every SDD skill (and a future test-protection hook) reads them instead of re-deriving them. The section loads on every session, so it must stay small and exact.

Explicit-only: the user must type `/sdd-init`; the model cannot invoke this skill. If the user says "go" or "run it" in chat, tell them to type the command themselves instead of trying to run it.

Why a gate: this skill edits a file the whole team reads. It shows the exact change first and writes only after an explicit yes.

## Boundaries

- Discovery is read-only. Writes happen only in step 5, after approval, and only to: the instruction file (the `SDD` section) and the specs directory (`README.md` or `.gitkeep`).
- Never commit, stage, amend, rebase or otherwise touch git history. Suggest a commit message at the end; the user commits.
- Never delete or edit project-level agents, other docs or sibling specs. Report them.
- Never invent a command. Every command in the section was confirmed to exist or is marked `none`.

## Workflow

### 1. Discover (read-only)

`$ARGUMENTS`, if given, is the specs directory and overrides discovery for it.

Read `references/discovery.md` and run it fully. Collect:

- Specs dir (existing candidate or proposal).
- Verify-all, test, lint, typecheck and build commands, each **confirmed to exist** (script present, binary on PATH or at a known toolchain location). Report missing ones as `none`; do not fabricate.
- Test-file glob patterns, derived from the tests that actually exist and the runner's config (several globs are fine).
- Commit convention (from `git log`), documentation language.
- Instruction-file target, chosen in this order:
  1. The file that already holds an `SDD` section.
  2. If `CLAUDE.md` exists and only imports another file via `@file` (for example `@AGENTS.md`), the **imported** file.
  3. Otherwise the one that exists (`CLAUDE.md` or `AGENTS.md`); if both exist and neither imports the other, ask which.
  4. If none exists, ask before creating `CLAUDE.md`.

### 2. Present findings

Show a compact table: setting, discovered value, source, confidence (confirmed / inferred / unknown). Also report the agents check (step 3). Keep it to one screen.

### 3. Check agents

- Global: `~/.claude/agents/spec-reviewer.md`, `test-writer.md`, `sdd-doc-reviewer.md` - report present or missing. Missing ones are reported, not created (they are installed with the global SDD set).
- Project-level: look for the same three names in the repo's `.claude/agents/`. A project agent shadows the global one of the same name: report each with the path and say that the user decides whether to remove it. Never delete.

### 4. Ask (only what the repo did not answer)

`AskUserQuestion`, at most 4 questions per round, recommended option first with the reason in its description. Typical: unknown/ambiguous specs dir, which verify command to use as "verify all" when several fit, a missing check (`none` vs. add a task later), test globs, instruction-file choice. State obvious answers as assumptions instead of asking (for example, a command resolved off-PATH: record its full path and say so). Do not ask what discovery already confirmed.

### 5. Propose, then apply

1. Fill `templates/sdd-section.md`. Drop a line only if its value is genuinely `none`, writing `none` rather than deleting the key for commands, so absence is explicit. Keep the whole section under about 25 lines; no prose beyond the template.
   When creating a brand-new instruction file, offer a 2-line header (project name + stack line) above the `## SDD` section so the file has context.
2. **Show the exact change**, not a description:
   - a unified diff of the instruction file (for a brand-new file the diff is the whole file; new section appended at the end, or, if a `## SDD` section exists, a diff that updates it in place, preserving any custom lines the user added and flagging them);
   - the specs-directory creation, with the content of the one file to be created (a 3-line `README.md` naming the `NNN-<slug>/` layout and the four documents, or an empty `.gitkeep` if the directory already has content).
3. Ask for approval with `AskUserQuestion` (apply / adjust / cancel). Apply **only** on an explicit yes. Anything else means adjust or stop.
4. After applying, re-read the file once to confirm the section is intact and nothing else changed.

### 6. Hand over

Reply with: what was written (paths), the settings recorded, checks that are `none`, agent findings (missing global, shadowing project agents), and a suggested commit message for the user to run. End with exactly: `Next: /sdd-spec-writer <idea or ticket>`. Only suggest it; never start it.

## Idempotency

Running again is safe: if an `SDD` section exists, treat it as the baseline, re-run discovery, and propose a diff only for values that changed or became confirmable. No differences means say so and write nothing. Never duplicate the section, and never reorder or remove lines the user added.

## Files in this skill

- `references/discovery.md`: shared project-discovery procedure (identical copy used by the other SDD skills). Read in step 1.
- `templates/sdd-section.md`: the `SDD` section template with `{{PLACEHOLDERS}}`.
