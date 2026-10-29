# Global instructions

My skills and agents live in `~/.agents` (`skills/`, `agents/`), a git repo synced across my computers. `~/.claude/skills` and `~/.claude/agents` are symlinks into it.

## Per-machine configuration

Nothing machine-specific is committed. A skill that needs local paths or settings reads a git-ignored `config.json` in its own folder; `config.example.json` next to it documents the keys. If a skill reports missing config, copy the example to `config.json` and edit it. Never hard-code absolute paths, usernames or hostnames in a skill or agent: add a config key instead.

## Documentation skills (`docs-*`)

For writing, auditing, migrating or scaffolding project documentation (PRD, DBDD, ADRs, overview, roadmap) use `docs-init`, `docs-author`, `docs-adr`, `docs-audit` and `docs-migrate`; the read-only `docs-auditor` agent is used by `docs-audit`. They work against a docs repo that holds `CONVENTIONS.md`, `templates/` and `guides/`, found via (in order) `--docs-root`, the current directory, a `.docs-root` file in a code repo, the `DOCS_ROOT` env var, or `docs_root` in `~/.agents/skills/docs-audit/config.json`.

## Spec-driven development (`sdd-*`)

Feature work follows `sdd-init` -> `sdd-spec-writer` -> `sdd-plan-writer` -> `sdd-task-writer` -> `sdd-executor`, with `sdd-reviewer` before approving any document. The subagents `test-writer`, `spec-reviewer` and `sdd-doc-reviewer` must be installed.
