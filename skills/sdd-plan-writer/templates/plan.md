Status: Draft

# Plan: <feature name>

Spec: `<relative path to spec.md>` (Status: Approved (<user>, <date>))

## Approach summary
<Short description of the chosen design and why it satisfies the spec's goals. 3-8 sentences.>

## Sources consulted
<Every project document and versioned reference read to produce this plan. "full" = read completely, "headings" = skimmed by headings, "summary" = read via a delegated read-only subagent.>

| Path / reference | Read | Why it matters |
|------------------|------|----------------|
| `docs/...` | full | <constraint or decision it contributed> |
| `doc/...` | headings | <relevance> |
| <instruction file> | full | <rules followed> |
| <versioned framework docs URL, version> | full | <API relied on> |
| <datasheet / PDF / image, page or figure> | full (p. N) | <constraint> |
| <broken symlink / unreadable doc> | not read | <reason> |

Installed versions checked: <framework/board/library: version (source: lockfile/manifest/cache), or "none relevant">.

Not consulted (and why): <paths skipped as irrelevant, or "none">.

## Architecture decisions
### D1: <title>
Decision: <what is decided>
Why: <rationale, tied to G#/AC#/E#/constraint or a source above>
Alternatives considered (not chosen): <X - reason>; <Y - reason>

### D2: <title>
...

## Architecture conformance
<How this design respects the layering/module/dependency rules found in the project's instructions and docs. One row per rule.>

| Rule (source) | How the plan complies |
|---------------|-----------------------|
| <rule> (`<path>`) | <compliance> |

## Components / files touched
| Path | Change | Notes |
|------|--------|-------|
| `path/to/file` | new / modify | <what and why> |

## Data models and interfaces
- <schemas, types, API/contract shapes, function signatures; no implementation bodies>
- Pinned observables: <every format, identifier, interface or accessor a test will assert, or a D# reference>

## Documentation impact
| Document | Required change | When |
|----------|-----------------|------|
| `<path>` | <what must be updated> | task / needs separate approval |

(Write "None" if no existing document is affected.)

## Risks and mitigations
- R1: <risk> -> <mitigation>

## Testing strategy
- Unit: ...
- Integration: ...
- E2E / contract / manual: ...
- Test locations and conventions follow: <existing tests/runner found in discovery>

## Verify commands
| Purpose | Command | Confirmed |
|---------|---------|-----------|
| Test | `<cmd>` | yes |
| Lint | `<cmd>` | yes |
| Typecheck | `<cmd>` | yes |
| Build | `<cmd>` | yes |
| Verify all | `<cmd>` | yes |
| <new harness command introduced by this plan> | `<cmd>` | unconfirmed (created by T#; see D#) |

(Note any layer without a runnable check.)

## Traceability
| ID | Criterion (short) | Component(s) | Test level | Also (optional) |
|----|-------------------|--------------|------------|-----------------|
| AC1 | <short> | `<path>`, ... | unit / integration / e2e / contract / manual | <secondary level, e.g. unit + manual> |
| E1 | <short> | ... | ... | |

## Environment assumptions validation
<Include only when the spec has [ENV] criteria or environment Assumptions. Omit otherwise.>

| Spec ref (AC#/A#) | Assumption | How / when validated on the real target | Early validating task | If it fails |
|-------------------|------------|-------------------------------------------|-----------------------|-------------|
| <AC#/A#> | <assumption> | <procedure, when> | <T# placeholder; task-writer schedules FIRST, Type: env-validation> | reopen spec |

## Bring-up and safe first run
<Include only when relevant (physical/deployed target, first run can cause damage or cost). Omit otherwise.>
- Order of power-on / enablement: ...
- How to limit damage if something is wrong: ...
- What a healthy first output looks like: ...
- Environment prerequisites for the README: ...

## Manual verification procedures
<Include only when the Traceability section has manual rows.>

### <AC#/E#>: <short>
1. <step> -> expected: <observable>

## Rollout / migration notes
- <feature flags, data migrations, backward compatibility, or "None">

## Assumptions
- <only present when the user overrode a prerequisite (record the override and the open items) or something was assumed; otherwise omit>
