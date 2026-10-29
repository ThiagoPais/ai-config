# Milestone report template

Print this at every `MILESTONE CHECKPOINT`, then ask: continue / adjust tasks / stop.

```markdown
## Milestone <M#>: <name> - checkpoint

(`<M#>` is the id in parentheses in the milestone heading of tasks.md.)

**Tasks done:** <T# list>  |  **Remaining in scope:** <T# list>  |  **Blocked:** <none | T#>  |  **Resolved this milestone:** <none | T#>

### Verify results
| Command | Result | Notes |
|---|---|---|
| <test> | pass/fail | <counts> |
| <lint> | pass/fail | |
| <typecheck> | pass/fail | |

### Reviewer findings
| Task | Verdict | Fix rounds (max 3 after the initial review) | Notable findings (severity, file:line) |
|---|---|---|---|

### Deviations from spec/plan
- <decision, why, proposed doc change> or "none"

### Open questions
- <question> or "none"

### Follow-ups (out of scope)
- <idea> or "none"

### Diff stat
<git diff --stat output since the milestone started>

### Commits
<committed with IDs | not committed: suggested messages below>
- <T#>: <message following the project's convention, containing the task ID>

### Next
Suggest continuing in a fresh session: progress.md and tasks.md carry the state.
```
