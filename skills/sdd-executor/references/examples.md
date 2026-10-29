# Worked example (reference only, non-normative)

How discovery resolves for the `app-dev-class` repository, the first pilot project. No rule in SKILL.md depends on this.

- Specs dir: `doc/specs/` (feature folders such as `001-...`, `002-...`); project docs under `doc/`.
- Instruction file: `AGENTS.md` (via `CLAUDE.md`). It holds the architecture and layering rules (domain-driven layout under `src/domains`, thin routes in `src/app`) and a rule to consult versioned framework docs before using Expo/React Native APIs (the executor reads it before implementing); the executor obeys these during implementation.
- Verify commands: from `package.json` scripts and `AGENTS.md`: `npx expo lint`, `npx tsc --noEmit`, plus the test scripts present (including emulator/rules tests under `tests/`). Each is confirmed to exist before use; the lockfile (`bun.lock`) picks `bunx` over `npx`.
- Commit style: from `git log` (conventional commits with ticket prefixes such as `feat(MAP-19): ...`); the task ID is added to the message.
- Test conventions: existing tests live under `tests/` (`*.test.js`, `*.test.mjs`); the test-writer reuses them.
- Task states: docs-only tasks carry `Tests: none (docs-only)` and skip the test-writer; `Owner: human` tasks (for example a manual check on a device or a console setting) stop the run until the person confirms.
