---
name: issue-manager
description: Turns a feature or requirement description into a well-structured GitHub issue (user story + numbered acceptance criteria, matching whatever style the target repo's existing issues already use), and validates whether a PR or branch actually implements an issue's acceptance criteria by reading the changed code, running the repo's tests/build/lint, and drafting a verification report as an issue comment. Use this whenever someone wants to "write up a user story", "turn these requirements into a GitHub issue", "create tickets for this feature", "check if PR #N actually implements issue #M", "validate this branch against its issue", "did we finish all the acceptance criteria", "close the loop on issue #X", or "write a QA/verification report on this implementation". Works on any GitHub-hosted repo — it learns the house style from the repo itself rather than assuming one. Always drafts issue bodies and verification reports for explicit human approval before calling create_issue, add_issue_comment, or gh issue create/comment — never posts to GitHub without confirmation first.
compatibility: Needs a way to talk to GitHub — either the `gh` CLI authenticated for the target repo, or a GitHub MCP server exposing tools like create_issue, add_issue_comment, get_issue, get_pull_request. Works with either or both; not tied to any specific project, org, or MCP server name.
---

# Issue Manager

Two related jobs, both centered on one idea: an issue's acceptance criteria are a contract, and this skill helps write that contract clearly and later check whether the code actually honors it.

1. **Draft issues from requirements** — turn a feature description into a user story with clear, checkable acceptance criteria, in the same style the repo already uses.
2. **Verify implementations against issues** — given a PR or branch, figure out which issue it's supposed to satisfy, actually check the code and run the checks, and report back per-criterion.

Both jobs end the same way: show the human the exact text before anything gets posted to GitHub. Comments and issues are visible, hard-to-reverse, and public to the team — a drafting mistake costs one edit, but a posted mistake costs a correction thread. There is no fast path around this step.

## Picking your GitHub access method

Before doing anything else, work out how you'll actually talk to GitHub for this repo:

- Run `ToolSearch` with a query like `"github issue"` or `"github pull request"` to see what MCP tools are already loaded. There may be more than one GitHub MCP server configured (e.g. an org one and a personal one) — if so, the org/owner that the target repo belongs to tells you which one to try first. A server whose token doesn't have access to a given repo will fail with a 403/404 or a permission-classifier denial; when that happens, try the other configured server before falling back further.
- If no MCP tool works (or none is configured), use the `gh` CLI (`gh issue view`, `gh issue create`, `gh issue comment`, `gh pr view`, `gh api ...`). It's usually already authenticated on the user's machine and is the most portable option — it doesn't depend on which MCP servers happen to be wired up in a given session.
- Figure out `owner/repo` from context: an explicit mention, or `git remote get-url origin` in the target repo's working copy, parsed for `github.com[:/]<owner>/<repo>`.

Whichever method works, keep using it consistently for the rest of the task rather than mixing tools per call — it keeps the reasoning about permissions simple.

## Job 1 — Draft an issue from requirements

**Goal:** turn a feature/bug description into an issue that reads like it was written by someone who already knows this repo's conventions.

1. **Learn the house style before writing anything.** Fetch the last handful of issues in the target repo (`list_issues` / `gh issue list --repo <owner>/<repo> --limit 10 --state all`, then read 2-3 full bodies via `get_issue` / `gh issue view <n>`). Look at:
   - Language (Portuguese, English, something else)
   - Title convention (e.g. a `[Feature]`/`[Bug]` prefix, a type label, conventional-commit-style prefixes, or nothing)
   - Body structure (headings used, whether there's a "user story" section and an "acceptance criteria" section, checkboxes vs. numbered lists, emoji in headings, etc.)

   If the repo has no prior issues to learn from, fall back to the generic default template in `references/issue-template-examples.md` and ask the user which language and level of formality they want — don't silently guess for an empty repo.

2. **Turn the requirement into a user story shape**: identify the actor, the action, and the benefit ("As a `<actor>`, I want `<action>`, so that `<benefit>`"), in whatever language the house style uses.

3. **Break the requirement into acceptance criteria that are each independently checkable** — the kind of criterion someone could look at a diff and say yes/no to, not a vague restatement of the goal. Group related sub-details as bullets under a numbered criterion, the way a real spec does. Let the *actual complexity of the requirement* set the count — don't force a fixed number of criteria just because a past example happened to have five.

4. **Draft the title + body** matching the learned style exactly (same emoji, same heading names, same language). See `references/issue-template-examples.md` for a worked example of the shape to aim for.

5. **Show the full draft to the user and wait for explicit approval** — treat requested edits as normal, not as a sign you got it wrong; requirements docs are often ambiguous and the user is the source of truth on intent.

6. **Only once approved**, create the issue with whichever GitHub access method you settled on, and give the user the resulting URL.

## Job 2 — Verify an implementation against its issue

**Goal:** given a PR number or a branch name, determine whether the linked issue's acceptance criteria are genuinely satisfied — not just plausible-looking, but actually implemented and passing.

### Step 1: Resolve the target and find the linked issue

- PR number given → fetch it (`get_pull_request` / `gh pr view <n> --json title,body,headRefName,baseRefName,url,closingIssuesReferences`).
- Branch name given, no PR → check `gh pr list --head <branch> --repo <owner>/<repo>`; if a PR exists, treat it as the PR case. If not, you'll diff the branch directly against its base and you'll need to ask which issue it targets (there's no PR description to read).
- To find the linked issue, prefer `closingIssuesReferences` from `gh pr view --json` when available — GitHub has already resolved this for you. Otherwise, run `scripts/extract_linked_issues.py` against the PR title + body to pull out `close(s|d)`/`fix(es|ed)`/`resolve(s|d) #N` references (handles bare `#N`, `owner/repo#N`, and full issue URLs). If nothing turns up, ask the user which issue this PR/branch is meant to satisfy — don't guess from vibes.

### Step 2: Read the issue's acceptance criteria

Fetch the full issue body (`get_issue` / `gh issue view <n>`) and parse out the acceptance criteria list. These are the checklist you'll score against.

### Step 3: Actually read the code — don't grade from the diff alone

For each acceptance criterion, find and **read the full contents** of the relevant files (not just the diff hunk — surrounding context often matters, e.g. whether a route has a component attached, whether a guard is actually wired into the router, whether an interceptor's error branch exists at all). A criterion can be satisfied by code that pre-dates this PR, and a criterion can look satisfied in the diff but be wired up wrong elsewhere — reading only the patch misses both cases.

### Step 4: Run the repo's actual checks

Detect what's available and run it, recording exact output (pass/fail counts, exact error messages) rather than paraphrasing:
- Node projects: check `package.json` `scripts` for `test`, `test:e2e`, `build`, `lint` and run whichever exist.
- Other ecosystems: look for the idiomatic equivalent — `pytest`/`tox`, `go test ./...`, `cargo test`/`cargo clippy`, a `Makefile` target, etc.
- If a build or lint step needs a prerequisite (codegen, migrations), run that first the same way you'd need to for a real contributor — don't report a failure that's actually just a missing setup step.

### Step 5: Score each criterion and draft the report

For each acceptance criterion, mark it met / partially met / not met (use whatever wording the issue itself uses if it's not in English — e.g. ✅ Atendido / ⚠️ Parcialmente atendido / ❌ Não atendido for a Portuguese issue), with a one-line reason citing the actual file. Then draft a report following the shape in `references/verification-report-example.md`:
- A per-criterion breakdown
- A test/build/lint results section with exact numbers
- A summary table of open items
- A closing line that promises only what you're actually about to do

**Do not promise a follow-up issue for something the user hasn't agreed should be tracked.** Some gaps are real bugs; others are "not built yet, as expected" or "we'll fix that as a quick internal cleanup, no need for a ticket." Ask the user to sort found gaps into "make a follow-up issue" vs. "not a problem" vs. "handle internally, no issue" before drafting the closing line and any follow-up issues — this session's own history is the cautionary example: an early draft flagged a not-yet-built dashboard route and an intentional "logout before switching accounts" behavior as bugs, and the user had to correct both.

### Step 6: Get approval, then post

Show the full draft report (and, separately, drafts of any agreed follow-up issues, using the same house-style template from Job 1) to the user. Only after explicit approval:
1. Post the verification comment on the original issue.
2. Create the agreed follow-up issues, each referencing the verification comment/date so the trail is easy to follow later.

## Reference files

- `references/issue-template-examples.md` — a generic default user-story template (for repos with no prior issues to learn style from), plus a worked Portuguese example showing the shape a good breakdown takes.
- `references/verification-report-example.md` — a full worked example of a verification report and a matching follow-up issue, showing the tone and structure to aim for.
- `scripts/extract_linked_issues.py` — pulls `closes/fixes/resolves #N` (and owner/repo#N, and full URL) references out of PR text. Run it as `python3 extract_linked_issues.py <file-or-'-'>`.
