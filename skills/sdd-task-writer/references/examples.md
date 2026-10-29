# Worked example (reference project only)

Non-normative. Shows how discovery resolves in the repository `app-dev-class`; none of this applies to other projects.

- Specs directory: `doc/specs/NNN-<slug>/` (existing specs 001 and 002 stay untouched).
- Instruction file: `AGENTS.md` (architecture and layering rules; "consult the versioned framework docs before using framework APIs"). Plan tasks should respect those layering rules; tasks only mount screens from route files and place business logic in domain modules.
- Verify commands: from `package.json` scripts and the instruction file: lint, typecheck, test commands; confirm each before use.
- Commit style: from `git log` (conventional commits with a ticket prefix); executor includes the task ID.

Condensed `tasks.md` excerpt for a hypothetical "group chat rename" feature:

```markdown
## Execution waves
| Milestone | Wave | Tasks | Notes |
| --- | --- | --- | --- |
| M1 | 1 | T1, T2 | independent, share no files |
| M1 | 2 | T3 | depends on T1 |

## Milestone 1 (M1): Data and rules
- [ ] **T1: Add rename operation to the chat service contract**
  - Covers: AC1, E1
  - Depends on: none
  - Files: <service file>, <service test>
  - Done when: `<test command> <service test>` passes, and an admin rename is visible to all members while an empty name is rejected with the documented error
  - Parallel: yes
  - Owner: agent
- [ ] **T2: Update access rules for rename**
  - Covers: AC2
  - Depends on: none
  - Files: <rules file>, <rules test>
  - Done when: `<rules test command>` passes, and the rule denies a rename by a non-admin member
  - Parallel: yes
  - Owner: agent
- [ ] **T3: Verify rename on a real device**
  - Covers: AC3
  - Depends on: T1
  - Files: `<glue file>`
  - Tests: none (hardware-glue): push delivery cannot be simulated
  - Done when: manual procedure "<name>" from the plan shows the renamed title on the second device
  - Parallel: no
  - Owner: human
  - Blocking: no

> MILESTONE CHECKPOINT: stop and report to the human.
```
