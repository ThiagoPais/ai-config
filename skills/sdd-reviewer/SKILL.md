---
name: sdd-reviewer
description: Independent adversarial pre-read of a spec.md, plan.md or tasks.md before the human approves it, delegated to a fresh read-only reviewer that did not write the document. Use whenever the user says "review this spec", "review the plan", "check tasks.md", "is this spec ready", "poke holes in the plan", "find gaps before I approve", "second opinion on the spec", "sdd review", or runs /sdd-reviewer, or is about to approve any SDD document, even if they never say "SDD". Returns a PASS/FAIL verdict with evidence-backed findings by severity and proposed edits; it never edits upstream documents and never approves anything.
argument-hint: "[file or feature folder] [spec|plan|tasks] [--light]"
---

# SDD reviewer

Give the human an independent pre-read of one SDD document before they approve it. This is the highest-leverage checkpoint in the chain: a flaw approved here is implemented faithfully, in a loop, at scale. The review is done by the `sdd-doc-reviewer` subagent, which has not seen how the document was written; that independence is the whole point, so never replace it with your own review or soften its output.

Target: `$ARGUMENTS`. This skill reviews and proposes; it does not approve and does not write documents from scratch.

## Step 1: Resolve the target

1. Parse `$ARGUMENTS` into an optional path, an optional kind (`spec`, `plan`, `tasks`) and an optional `--light` flag. `--light` means `Rigor: light` (blockers and majors only, minors as a count); otherwise `Rigor: standard`. Suggest `--light` for experimental or throwaway features, where minors are noise.
2. If the path is a file named `spec.md`, `plan.md` or `tasks.md`, that is the document and its kind comes from the filename (an explicit kind that disagrees: ask).
3. If the path is a feature folder, pick the most advanced document that is still `Status: Draft` (first line), in the order `tasks.md`, `plan.md`, `spec.md`. If an explicit kind was given, use that file. If nothing is Draft, or the choice is ambiguous, ask which document to review (propose the most advanced one).
4. If `$ARGUMENTS` is empty, run discovery (below), list feature folders under the specs directory, and ask which to review, proposing the most recently changed one with a Draft document.
5. Reviewing an already Approved document is allowed (late audit); say so in the summary and never change its status.

## Step 2: Locate upstream and project docs (read-only)

Run `references/discovery.md` only as far as needed: the specs directory (to resolve folders) and the project's documentation paths and instruction files. Do not resolve verify commands or conventions beyond what the brief needs.

- `spec` kind: no upstream.
- `plan` kind: upstream is `spec.md` in the same folder.
- `tasks` kind: upstream is `spec.md` and `plan.md`.
- Project docs: an index of paths (instruction files, `docs/`, `doc/`, ADRs, README and architecture or data/contract docs). Pass paths, not contents. For a `spec`, pass them too; the reviewer may check for contradictions.

If an upstream document is missing, review anyway and tell the reviewer it is absent; a missing upstream is itself a finding for the human.

## Step 3: Delegate

Fill `references/review-brief.md` for the document kind and launch the `sdd-doc-reviewer` subagent with only: kind, `Rigor`, document path, upstream paths, project docs paths, and the brief's instructions. Give it paths, not summaries.

The brief lists document paths only. Never include the author's notes, `progress.md`, logs or scratch files, even as "context": the reviewer must judge the document, not the author's intent.

Never pass your own opinions, the author's reasoning, the conversation that produced the document, or hints about what is probably fine. Why: a reviewer primed with the author's intent will rationalise the gaps instead of finding them.

## Step 4: Read the verdict critically

Read the reply before relaying it. Agents that review documents drift toward agreement.

- A `PASS` with zero findings on a non-trivial document (more than a handful of criteria or tasks) is suspect. Re-brief once with the "stricter pass" instruction in `references/review-brief.md` and say in the summary that you did so. Use the second verdict; do not loop further.
- Findings lacking a location or evidence are incomplete: ask the agent for evidence once, or mark the finding "unverified" when presenting it.
- Spot-check one or two cited `path:line` references before presenting; discard or flag any that do not hold.
- Keep the agent's severities. Do not downgrade a blocker or drop findings because they look nitpicky; surface your own disagreement as a note beside the finding.

## Step 5: Present

Show the user, in this order:

1. **Verdict** (PASS or FAIL), the document and kind, its current Status line, and whether a re-brief happened.
2. **Findings** grouped by severity: blockers, then majors, then minors. Each: number, location, problem, evidence, suggested change.
3. **Questions for the human**: decisions only they can make (scope, trade-offs, intent) that are not already a finding; merge overlaps into the finding. Keep the list short and mark each question with a safe default as `non-blocking (default: X)`.
4. **Proposed edits**: the exact change per finding as a short diff or replacement text, against the reviewed document only. If a finding belongs upstream (for example a plan flaw caused by the spec), propose the upstream change as text but mark it "upstream, for you to apply or to run the owning skill".

End every report with the reviewer's line `Remaining: <n> blockers, <m> majors, <k> minors — approve now?` (a recommendation, never an approval). Offer, never apply. Ask which findings the user wants applied.

## Step 6: Apply only on request

Only when the user names specific findings (or says "apply all"):

1. Edit the reviewed document only, and only for those findings.
2. Set or keep the first line as `Status: Draft`. Never write `Approved`, and never mark questions RESOLVED on the human's behalf unless they gave the answer in this chat.
3. Never edit upstream documents, project docs, or `progress.md`.
4. Show a concise change list, and offer a re-review to confirm (a fresh reviewer run, not you).
5. Also offer, optionally, a one-pass consistency check over the AC/E cross-references (IDs cited in goals, plan table, tasks coverage) after the fixes, since edits often break references.

### Mapping the user's answers

- Answers to the Questions for the human count as a request to apply the findings those answers settle. Apply those findings only; leave the rest.
- An answer that is itself a new scope item is not an AC. Record it as a `Q#` with options in the spec, via the spec writer skill, and let the human resolve it.
- A risk the human accepts goes to the spec's Constraints with owner and date.

### Re-review rounds

Stop when there are no blockers and the human accepts the remaining minors. Further rounds past that point polish without reducing risk. End each round's report with the `approve now?` line; for experimental features suggest `--light`.

## Step 7: Hand off

- After `PASS`: remind the user that approval is their explicit decision and that a pass is a pre-read, not a guarantee. Only suggest the next command, never run it: spec -> `/sdd-plan-writer <feature folder>`; plan -> `/sdd-task-writer <feature folder>`; tasks -> `/sdd-executor <feature folder> M1`.
- After `FAIL`: suggest fixing the blockers and majors (by the owning writer skill or by the applied edits above) and re-running `/sdd-reviewer <feature folder> <kind>`.

## Guardrails

- Read-only on everything except the reviewed document, and only on request.
- Never approve, and never present PASS as approval.
- Never review the document yourself in place of the subagent; if the subagent cannot be launched, say so and stop rather than improvising.
- Never invent findings to look thorough, and never hide the agent's.
- Do not write or change implementation code.
