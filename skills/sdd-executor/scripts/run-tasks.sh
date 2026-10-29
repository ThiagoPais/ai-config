#!/usr/bin/env bash
# run-tasks.sh - OPTIONAL unattended outer loop for sdd-executor. OFF by default.
# Use only after the interactive flow (/sdd-executor) has proven stable, on a
# feature branch or git worktree. It never pushes. It stops on the first Blocked task.
#
# Usage: run-tasks.sh <feature-dir> <T#> [T# ...]
# Env:   SDD_ALLOWED_TOOLS   REQUIRED. Comma list of extra --allowedTools entries so the
#                            project's verify commands can run, e.g.
#                            'Bash(<test command>:*),Bash(<lint command>:*)'
#        SDD_COMMIT=1        let each task commit (git add/commit allowed). Default: no
#                            commits; changes stay in the working tree and the suggested
#                            commit message is printed.
#        SDD_MAX_BUDGET_USD  per-task spend cap (default 5)
#        SDD_TASK_TIMEOUT    wall-clock cap per task, e.g. 30m (default 30m)
#        SDD_ALLOW_DEFAULT_BRANCH=1  skip the default-branch refusal (not advised)
# Caps: `claude --help` offers --max-budget-usd but no --max-turns, so the
#       iteration cap (3 fix rounds after the initial review) lives in the prompt and a
#       wall-clock timeout backs it up.
set -euo pipefail
shopt -u patsub_replacement 2>/dev/null || true   # bash 5.2: keep '&' literal in substitutions

die() { echo "$*" >&2; exit 2; }
usage() { die "Usage: $0 <feature-dir> <T#> [T# ...]"; }
[ "$#" -ge 2 ] || usage
FEATURE_DIR="${1%/}"; shift
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/../references/headless-prompt.md"

command -v claude >/dev/null || die "claude CLI not found"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not inside a git repository"
[ -f "$PROMPT_FILE" ] || die "Missing $PROMPT_FILE"
[ -n "${SDD_ALLOWED_TOOLS:-}" ] || die "SDD_ALLOWED_TOOLS is required: list the verify commands the run may execute, e.g. SDD_ALLOWED_TOOLS='Bash(<test command>:*),Bash(<lint command>:*)'. Without them the headless session cannot run the tests."

for f in spec.md plan.md tasks.md progress.md; do
  [ -f "$FEATURE_DIR/$f" ] || die "Missing $FEATURE_DIR/$f"
done
for f in spec.md plan.md tasks.md; do
  head -n 1 "$FEATURE_DIR/$f" | grep -qE '^Status:[[:space:]]*Approved \(.+\)' \
    || die "$FEATURE_DIR/$f does not start with 'Status: Approved (...)'; refusing to run (overrides are interactive-only)."
done
# Strict: every Q# must be marked RESOLVED (or the section says None).
if grep -E '^[[:space:]]*([-*][[:space:]]+)?\**Q[0-9]+[:.)]' "$FEATURE_DIR/spec.md" | grep -qv 'RESOLVED'; then
  die "spec.md has unresolved Q# entries; refusing to run."
fi

# Agents the per-task process delegates to.
REPO_ROOT="$(git rev-parse --show-toplevel)"
for a in test-writer spec-reviewer; do
  [ -f "$HOME/.claude/agents/$a.md" ] || [ -f "$REPO_ROOT/.claude/agents/$a.md" ] \
    || die "Subagent '$a' not found in ~/.claude/agents or $REPO_ROOT/.claude/agents."
done

# Print the block of a task (its checkbox line plus indented fields).
task_block() {
  awk -v id="$1" '
    $0 ~ "^[[:space:]]*[-*][[:space:]]+\\[[ xX]\\][[:space:]]+\\**" id "[^0-9]" { f=1; print; next }
    f && /^[[:space:]]*[-*][[:space:]]+\[[ xX]\]/ { exit }
    f && /^#|^>/ { exit }
    f { print }
  ' "$FEATURE_DIR/tasks.md"
}
is_ticked() { grep -qE "^[[:space:]]*[-*][[:space:]]+\[[xX]\][[:space:]]+\**$1([^0-9]|$)" "$FEATURE_DIR/tasks.md"; }

for t in "$@"; do
  [[ "$t" =~ ^T[0-9]+$ ]] || die "Invalid task id: $t (expected T<number>)"
  [ -n "$(task_block "$t")" ] || die "Task $t not found in $FEATURE_DIR/tasks.md"
  if task_block "$t" | grep -qiE 'Owner:[[:space:]]*\**human'; then
    die "Task $t is Owner: human (manual-only); do it by hand or run it interactively. Refusing."
  fi
done

# Never run on the default branch.
BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || echo DETACHED)"
DEFAULT="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' || true)"
if [ "${SDD_ALLOW_DEFAULT_BRANCH:-0}" != "1" ]; then
  case "$BRANCH" in
    "$DEFAULT"|main|master|trunk|develop|DETACHED)
      die "Refusing to run on '$BRANCH'. Create a feature branch or worktree first." ;;
  esac
fi
# The feature dir is excluded: progress.md/tasks.md legitimately change between tasks.
if [ -n "$(git status --porcelain -- . ":(exclude)$FEATURE_DIR")" ]; then
  die "Working tree is not clean (outside $FEATURE_DIR). Commit or stash first."
fi

BUDGET="${SDD_MAX_BUDGET_USD:-5}"
TASK_TIMEOUT="${SDD_TASK_TIMEOUT:-30m}"
BASE_TOOLS="Read,Grep,Glob,Edit,Write,Agent,Bash(git status:*),Bash(git diff:*),Bash(git log:*),Bash(git hash-object:*)"
if [ "${SDD_COMMIT:-0}" = "1" ]; then
  BASE_TOOLS="$BASE_TOOLS,Bash(git add:*),Bash(git commit:*)"
  COMMIT_POLICY="Commit on the current branch with the task ID in the message, following the project's commit convention (the user opted in to commits for this run)."
else
  COMMIT_POLICY="Do not commit: leave the changes in the working tree and print the suggested commit message (project convention, containing the task ID)."
fi
ALLOWED="$BASE_TOOLS,$SDD_ALLOWED_TOOLS"
DISALLOWED="Bash(git push:*)"   # defense in depth: the script never pushes

TIMEOUT_CMD=()
if command -v timeout >/dev/null; then TIMEOUT_CMD=(timeout "$TASK_TIMEOUT")
elif command -v gtimeout >/dev/null; then TIMEOUT_CMD=(gtimeout "$TASK_TIMEOUT")
else echo "Warning: no timeout/gtimeout found; the wall-clock cap is NOT enforced (only the budget cap)." >&2
fi

TEMPLATE="$(awk '/^```text$/{f=1;next} /^```$/{if(f)exit} f' "$PROMPT_FILE")"
[ -n "$TEMPLATE" ] || die "No \`\`\`text block found in $PROMPT_FILE"

snapshot_tree() { # tree of the working tree incl. untracked files; real index untouched
  local idx; idx="$(mktemp -u)"
  GIT_INDEX_FILE="$idx" sh -c 'git read-tree HEAD && git add -A && git write-tree'
  rm -f "$idx"
}
count_blocked() { grep -cE "^[-*[:space:]]*Blocked: ${1}([^0-9]|$)" "$FEATURE_DIR/progress.md" || true; }

echo "Branch: $BRANCH | budget/task: \$$BUDGET | timeout/task: $TASK_TIMEOUT | commits: $([ "${SDD_COMMIT:-0}" = 1 ] && echo yes || echo no) | never pushes"

for TASK in "$@"; do
  # Dependencies must already be ticked (earlier tasks of this run count once ticked).
  deps="$(task_block "$TASK" | grep -iE 'Depends on:' | grep -oE 'T[0-9]+' || true)"
  skip=0
  for d in $deps; do
    is_ticked "$d" && continue
    # A deferred human task (Owner: human, Blocking: no) leaves its dependents pending.
    if task_block "$d" | grep -qiE 'Owner:[[:space:]]*\**human' \
       && task_block "$d" | grep -qiE 'Blocking:[[:space:]]*\**no'; then
      echo "Skipping $TASK: depends on $d (deferred human task, Blocking: no)." >&2
      skip=1
    else
      die "Task $TASK depends on $d, which is not ticked. Refusing."
    fi
  done
  [ "$skip" -eq 0 ] || continue

  echo "=== Running $TASK ==="
  GIT_BASE="$(snapshot_tree)"
  PROMPT="$TEMPLATE"
  PROMPT="${PROMPT//<FEATURE_DIR>/$FEATURE_DIR}"
  PROMPT="${PROMPT//<TASK-ID>/$TASK}"
  PROMPT="${PROMPT//<BRIEFS_DIR>/$SCRIPT_DIR/../references/briefs}"
  PROMPT="${PROMPT//<GIT_BASE>/$GIT_BASE}"
  PROMPT="${PROMPT//<COMMIT_POLICY>/$COMMIT_POLICY}"

  before="$(count_blocked "$TASK")"
  rc=0
  ${TIMEOUT_CMD[@]+"${TIMEOUT_CMD[@]}"} claude -p "$PROMPT" \
    --max-budget-usd "$BUDGET" \
    --allowedTools "$ALLOWED" \
    --disallowedTools "$DISALLOWED" \
    --permission-mode default || rc=$?

  after="$(count_blocked "$TASK")"
  if [ "$after" -gt "$before" ]; then
    echo "Task $TASK is blocked. Stopping for human review." >&2
    exit 1
  fi
  if [ "$rc" -ne 0 ]; then
    echo "claude exited with status $rc on $TASK (budget/timeout/error). Stopping." >&2
    exit "$rc"
  fi
  if ! is_ticked "$TASK"; then
    echo "Task $TASK was not ticked in tasks.md. Stopping for human review." >&2
    exit 1
  fi
done

echo "All requested tasks finished. Review the diff and progress.md. Nothing was pushed."
