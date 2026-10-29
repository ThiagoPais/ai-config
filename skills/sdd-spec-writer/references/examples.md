# Worked example: the `app-dev-class` repository

Non-normative. This is the only file in the skill that may mention project-specific details. Nothing in `SKILL.md` depends on it, and none of it should be carried to other projects.

## How discovery resolves in this repository

| Discovery step | Result here |
| --- | --- |
| Instruction files | `CLAUDE.md` imports `AGENTS.md`: an Expo / React Native mobile app, Domain-Driven Design layout under `src/domains/<domain>`, thin routes in `src/app/`, rule to consult the versioned Expo docs before touching Expo or React Native APIs |
| Specs directory | `doc/specs/` (the project uses `doc/`, not `docs/`); existing folders `001-...`, `002-...` are left untouched, so a new feature becomes `003-<slug>` |
| Verify commands | From `package.json` scripts and `AGENTS.md`: `npx expo lint`, `npx tsc --noEmit`; tests under `tests/` (rules and emulator tests) |
| Commit convention | From `git log`: conventional commits with a ticket scope, e.g. `feat(MAP-19): ...` |
| Documentation language | English, matching `doc/` |

Implications for the interview: do not ask which framework, test runner or folder to use; the repository answers it. Do ask about product behavior (roles, limits, failure cases).

## Illustrative spec excerpt

Idea: "let group admins rename a group chat and change its picture".

```markdown
Status: Draft

# Spec: Edit group information

## Problem
Group chats are created with a name and picture that cannot be changed afterwards.
Members end up with outdated or misspelled group names and have no way to correct them.

## Goals
- G1: Group admins can change the group's name and picture.
- G2: All members see the change without reinstalling or re-creating the group.

## Non-goals
- NG1: Editing a direct (one-to-one) chat's information.
- NG2: Change history or audit log of edits.

## Acceptance criteria
- AC1: Given a group admin, when they submit a new non-empty name, then every member sees the new name in the group header and in the chat list (observation point: header and list elements).
- AC2: Given a member who is not an admin, when they try to change the name, then the change is rejected and the name stays the same.
- AC3 [ENV]: Given a group admin on a connected device, when they submit a new picture, then the picture is replaced for all members within the delay in A1 (A1).

## Assumptions
- A1: Changes propagate to online members within 5 seconds — source: model-proposed

## Edge cases and error handling
- E1: Name is empty or only whitespace -> rejected, the previous name is kept, the admin sees an error.
- E2: Name longer than the limit in Q1 -> rejected with a length message.
- E3: Two admins rename at the same time -> the last accepted change wins and both see the final value.
- E4: The admin loses connectivity while saving -> the change is not applied and the admin is told to retry.

## Documentation impact (flags only)
- Data model document -> new editable fields on the group; permission rules for who may edit them.

## Open questions
- Q1: What is the maximum name length? - product owner
```

Things this excerpt demonstrates:

- Criteria describe what a member observes, not how rules or services are structured.
- The role restriction (AC2) is its own criterion because it is a distinct testable behavior.
- The observation point is named in each AC; the `[ENV]` criterion references an `A#`, and the model-proposed value is listed under Assumptions for confirmation.
- The unknown limit stays an open `Q1` (the plan cannot start until it is marked RESOLVED) instead of an invented number.
- The data-model impact is flagged under documentation impact; designing it is left to the plan phase.
