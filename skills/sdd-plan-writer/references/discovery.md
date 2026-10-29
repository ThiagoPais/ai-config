# Project discovery (shared procedure)

These skills are global and must work in any repository. Never assume a stack, folder layout or convention: read them from the project. Run this procedure read-only at the start, keep the results in mind, and only ask the user about what the repository cannot answer.

## 1. Instruction files
Read `CLAUDE.md`, `AGENTS.md` and equivalents if present (`.cursorrules`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`). Follow the rules they give, including rules like "consult the versioned docs before using library X" or architecture/layering constraints. If they contain an `SDD` section, it is authoritative for the settings below.

## 2. Specs directory
In order: the SDD section of the instruction file; the first existing of `specs/`, `docs/specs/`, `doc/specs/`, `.specs/`; otherwise ask once and propose `docs/specs/` (or `doc/specs/` if the project uses `doc/` rather than `docs/`).
Feature folders are `<specs-dir>/NNN-<slug>/`. `NNN` = highest existing number + 1, zero-padded to 3 digits. Leave existing folders with a different shape untouched.

## 3. Stack and verify commands
From the SDD section / instruction files first; else from manifests: `package.json` scripts, `angular.json`, `nest-cli.json`, `pyproject.toml`, `tox.ini`, `Makefile`, `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml`, `*.csproj`, `composer.json`, `Gemfile`, embedded/hardware manifests (`platformio.ini`, `CMakeLists.txt` + `sdkconfig`, Arduino sketches or `Makefile`), and the package manager lockfile (to pick `npm`/`yarn`/`pnpm`/`bun`).
Resolve: test, lint, typecheck, build and a single "verify all" command. Confirm each command resolves before relying on it: script present, and the binary on PATH or at a known toolchain location (IDE/extension-managed installs are often off-PATH). If it is found only off-PATH, record the full path or ask the user how they invoke it. A missing check is reported, never invented.
Tests that need hardware (a board, a device, an attached peripheral) are `manual`. Use a host/native test environment when the project defines one; otherwise the automated test check is `none`.
Facts about the target environment (board, device, runtime or OS version) read from a manifest are tagged `inferred`; confirm them with the user when a spec or plan depends on them, since manifests often hold defaults or stale values.
Check the installed versions of frameworks the design depends on (lockfile, manifest, package cache) even if no instruction file says so, whenever the API differs across major versions: the installed version, not the latest docs, defines what code is valid.

## 4. Test conventions
Locate existing tests and the runner: patterns such as `*.spec.*`, `*.test.*`, `test_*.py`, `*_test.go`, `src/test/**`, `tests/**`, `__tests__/`. Note framework, fixtures, mocking style and where new tests belong. Reuse them; never introduce a second framework.

## 5. Commit convention
Read recent `git log --oneline` (conventional commits, ticket prefixes, scopes). Follow it and include the task ID where the executor commits. If no convention can be established (few or no commits), the value is `none established`; do not invent one.

## 6. Documentation language
Match the language of the existing project docs; default to English. When the only existing docs are not in the language the user is using, ask explicitly which language the SDD documents should use: matching the existing docs would often be the wrong default.

## 7. Templates
If the project has templates (`<specs-dir>/_templates/*.md`), use them; otherwise use this skill's `templates/`.

## 8. Unreadable, binary or non-text docs
Enumerate documentation by extension, case-insensitively (`.PDF` = `.pdf`): text formats (`.md`, `.mdx`, `.txt`, `.rst`, `.adoc`) plus `.pdf`, images (`.png`, `.jpg`, `.jpeg`, `.svg`, `.gif`) and datasheets. Check files tracked by git as well as those on disk.
For every file in the index that cannot be opened (dangling symlink, binary, no extractable text):
1. List it explicitly.
2. Try a text extractor (e.g. `pdftotext`) or, for images, the Read tool.
3. If that fails, ask the user where the real file is (a dangling symlink often points outside the repo).
4. Record it in the Sources consulted list as "not read" with the reason.
Never skip a document silently: an unread domain document leaves the work ungrounded. Evidence taken from non-text docs is cited by page or figure.

## 9. Unknowns
If something cannot be discovered, ask once (`AskUserQuestion`, recommended option first) and offer to record the answer in an `SDD` section of the project's instruction file. Do not write to that file without approval.

## Document conventions (all SDD skills)
- Files: `spec.md`, `plan.md`, `tasks.md`, `progress.md`.
- IDs: `G`, `NG`, `US`, `AC`, `E`, `Q`, `A` (spec); `D`, `R` (plan); `T`, `M` (tasks).
- First line of `spec.md`, `plan.md` and `tasks.md`: `Status: Draft | Approved (<user>, <date>)`. Always cite it in this canonical parenthesized form, and read it from the first line. Only the human's explicit yes changes Draft to Approved; the writing skill never does so by itself. A document with no Status line (legacy) counts as Draft. A downstream skill refuses a non-Approved upstream document unless the user explicitly overrides; it records the override (plan.md "Assumptions", tasks.md `Overrides:` line).
- Open questions are strict: every `Q#` must be marked RESOLVED (`Qn: <question> -> RESOLVED (<date>): <answer>`) before plan, tasks or execution proceed; `None` when there are none.
- Any edit of an Approved document by its writing skill resets it to `Status: Draft`: a changed document needs a new approval.
- Downstream skills never edit upstream documents; they propose the exact change and wait for approval.
- Questions: `AskUserQuestion`, at most 4 per round, recommended option first, never ask what the repo answers.
- Each skill ends with a short summary and a review request, and only *suggests* the next command; it never chains automatically.
- Status line: replace line 1 in place; e.g. `Status: Draft` becomes `Status: Approved (<git user.name>, <YYYY-MM-DD>)`.
- Removing an ID: never renumber or reuse; leave a tombstone line, e.g. `G5: removed (<reason>); ID not reused`. A removed `Q#` tombstone carries RESOLVED so the strict-questions rule passes: `Q3: removed (<reason>); ID not reused -> RESOLVED (<date>)`.
- The `--light` flag is recognized only by sdd-reviewer and sdd-executor; other skills ignore it.
