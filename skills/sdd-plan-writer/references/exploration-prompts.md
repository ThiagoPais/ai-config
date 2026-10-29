# Exploration briefs for subagents

Use `Explore` subagents (read-only). They know only what you put in the brief, so give the feature's essentials, a narrow question, the paths to look at, and the output shape. Launch up to 3 in parallel when the questions are independent; subagents cannot spawn subagents. Treat results as leads: open the files your design depends on yourself.

Fill the `<...>` placeholders from the spec and discovery. Never paste the whole spec; give the relevant goals, `AC#` and entities.

## A. Documentation sweep brief

```
Read-only task. Do not modify any file.

Context: we are planning the feature "<feature name>": <2-3 sentence summary of goals and the entities/roles involved>. Relevant spec criteria: <AC#/E# headline list>.

Documents to review: <list of paths or directory, e.g. a partition of the index>.

For EACH document return one entry:
- path
- title and a one-line purpose
- read depth you achieved (full | headings | not read, with reason; for PDFs/images cite page or figure)
- constraints, rules, contracts or decisions in it that a design for this feature must respect (quote the rule briefly and give section/heading or line)
- anything in it that conflicts with the feature, or that will need updating if the feature ships
- relevance: high | medium | none

Then add:
- conflicts between documents you noticed (path vs path)
- documents you could not read or that looked relevant but incomplete

Be concise; no design proposals. Report facts with path:line references.
```

## B. Existing patterns and reuse

```
Read-only task. Do not modify any file.

Context: planning "<feature name>": <summary>. We need to add <capability> in the area of <module/folder>.

Find and report, with path:line references:
1. How comparable features are structured today (files, layers, naming, wiring/registration).
2. Reusable utilities, components, services, types or helpers that this feature should use instead of creating new ones.
3. Conventions to follow (error handling, logging, validation, state/data access, configuration).
4. Where new code of each kind would naturally live according to existing structure.

Search breadth: <medium | very thorough>. Report only what you verified in code; say "not found" explicitly when something does not exist.
```

## C. Affected modules and integration points

```
Read-only task. Do not modify any file.

Context: planning "<feature name>": <summary>. The feature will change or depend on: <entities / endpoints / screens / jobs>.

Report, with path:line references:
1. Every module, file or entry point that reads or writes <entity/contract> today.
2. Public interfaces (signatures, schemas, routes, events) that the feature must stay compatible with.
3. Cross-module dependencies and any layering/boundary rules visible in the code (imports that are forbidden or conventional).
4. Configuration, permissions or access rules involved.
5. Anything fragile: global state, shared mutable data, known TODO/FIXME near these areas.

Do not propose a design.
```

## D. Test setup

```
Read-only task. Do not modify any file.

Context: planning "<feature name>". Verify commands discovered: <commands or "unknown">.

Report, with path:line references:
1. Test framework(s), runner config and how tests are invoked (exact commands).
2. Where tests live and how they are named, per level (unit, integration, e2e, contract).
3. Fixtures, mocks, factories, emulators or test servers already available and how they are started.
4. Gaps: layers touched by this feature that have no runnable test setup.
5. Lint, typecheck and build commands that exist (confirm they are defined, do not run long jobs).

Say "not found" explicitly rather than guessing.
```

## E. Versioned framework/library docs (only when project rules require it)

Do this yourself or via a general-purpose agent with web access when the instruction files require consulting versioned docs. Brief:

```
Read the installed version of <package/board/SDK> from <manifest, lockfile or package cache path>. Using the documentation location the project instructions point to (<URL pattern / index>), find the current, version-matched documentation for <API/feature>. Report: exact API names and signatures for that version, deprecations or renames relative to common older usage, and the URL of each page used. Do not answer from memory.
```

## Brief-writing tips

- One question per subagent beats a broad "explore everything".
- Ask for paths and line numbers; summaries without evidence cannot be checked.
- Ask for "not found" explicitly; it prevents invented patterns.
- Keep the brief free of your design hypotheses so results are not biased toward them.
