# Writing acceptance criteria and edge cases

The point of an acceptance criterion is that two people (or a test and a reviewer) would independently reach the same verdict. If a criterion cannot fail, it is not a criterion.

## Contents

1. Anatomy
2. Testability checks
3. Rewriting vague statements
4. Spec level vs plan level
5. Edge cases
6. Coverage and sizing
7. Anti-patterns

## 1. Anatomy

`ACn: Given <context>, when <action>, then <observable result>.`

- **Context**: the state that matters (role, existing data, setting). Include only what changes the outcome.
- **Action**: one actor, one trigger.
- **Result**: something a test can assert or a person can see: a value, a message, a state change, an absence, a count, a status.
- **Observation point**: say where the result is observed (output line, signal, stored row, API response, UI element). A result with no observation point cannot be checked; the interface must be one the spec specifies.
- Optionally append the IDs it serves: `(G1, US2)`.
- Tag `[ENV]` when it depends on runtime, transport, host tooling, power, process lifetime or other environment behaviour, and reference the `A#` that records the assumption.

One behavior per criterion. If the sentence needs "and then also", split it.

## 2. Testability checks

For each criterion ask:

1. What exact test would fail if this were broken? If you cannot describe one, rewrite it.
2. Is the expected result specific (a value, text, state) rather than a quality ("works", "is handled")?
3. Does it hold regardless of how the feature is built? If it names a technology or internal structure, it is a plan detail.
4. Can it be checked without reading the implementation? An observer at the system's boundary should be able to decide.
5. Is the numeric bound reachable given the stated limits and time constants? Do a quick calculation of what the number means; an unreachable or trivially-true bound is a defect.
6. Did the number come from the user? If not, it is a model-proposed value: list it under Assumptions.

## 3. Rewriting vague statements

| Vague | Testable |
| --- | --- |
| The page loads quickly | Given a list of 1,000 items, when the page opens, then the first rows are visible within 2 seconds on the reference device |
| Invalid input is handled | Given an empty name, when the user submits, then the submission is rejected and the message "Name is required" is shown next to the field |
| Only admins can remove members | Given a non-admin member, when they request to remove another member, then the request is refused and the member list is unchanged |
| It is secure | Given an unauthenticated visitor, when they request the resource, then they receive an authorization failure and no data from the resource |
| Works offline | Given no connectivity, when the user creates an item, then it appears in the list marked "pending" and is sent once connectivity returns |

When no honest number or observable exists yet, do not fake one: record a `Q#` ("What latency is acceptable?"). Every `Q#` must be marked RESOLVED before the plan phase can run, so ask the owner early.

## 4. Spec level vs plan level

The spec says what is observable; the plan says how it is achieved.

| Spec (keep) | Plan (leave out) |
| --- | --- |
| "A removed member can no longer read new messages" | "Add a check in the access-control layer" |
| "Search returns results within 1 s for 10k records" | "Create an index on the name column" |
| "Changes made on one device appear on the other" | "Use a realtime subscription" |

If the user insists on a technology, ask whether it is a true constraint (mandated by the organization, an existing contract) or a preference. Constraints go under Constraints; preferences are passed to the plan phase as notes.

## 5. Edge cases

Use `E#: <input or condition> -> <expected behavior>`. Walk these categories and keep only the ones that can actually occur here:

- empty / missing / first use
- duplicate or repeated action
- boundary values (min, max, exactly at limit)
- concurrent changes by two actors
- insufficient permission, or permission revoked mid-flow
- dependent data removed or unavailable
- partial failure, timeout, offline
- invalid or hostile input

An edge case is not a second acceptance criterion in disguise: use `AC` for the main behaviors and `E` for deviations from them. Both must be testable.

## 6. Coverage and sizing

- Every goal and user story is covered by at least one `AC`. Check by listing them side by side.
- Every `AC` serves a goal or story; an orphan criterion signals scope creep or a missing goal.
- Aim for a handful of sharp criteria per goal. More than about 15 `AC` in one spec usually means two features; propose a split.
- Keep IDs stable. After approval, add new IDs at the end instead of renumbering.

## 7. Anti-patterns

- **Solution-first**: "Add a toggle button" is a design; the requirement is what the user must be able to do.
- **Adjective criteria**: fast, intuitive, robust, secure, seamless, user-friendly.
- **Compound criteria**: several behaviors joined by "and", impossible to tell which part failed.
- **Negative-only**: "must not crash"; state the positive expected outcome as well.
- **Hidden decisions**: choices (limits, defaults, wording) silently baked in; surface them under Assumptions (`A#`, with source) or as a `Q#`.
- **No observation point**: "the system stays safe" with nothing that shows it; name where it is seen.
- **Copying the implementation**: criteria written by reading existing code only describe what exists, not what is needed.
