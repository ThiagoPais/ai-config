#!/usr/bin/env bash
# Link this repo into the agent tools' config folders. Safe to re-run.
# Usage: ./install.sh [--uninstall]
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
claude="${CLAUDE_HOME:-$HOME/.claude}"
mode="${1:-install}"

link() { # target link_path
  local target="$1" dst="$2"
  if [ "$mode" = "--uninstall" ]; then
    if [ -L "$dst" ]; then rm "$dst" && echo "removed  $dst"; fi
    return 0
  fi
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "SKIP     $dst exists and is not a symlink (move it away first)" >&2
    return 0
  fi
  mkdir -p "$(dirname "$dst")"
  ln -sfn "$target" "$dst" && echo "linked   $dst -> $target"
}

link "$here/skills" "$claude/skills"
link "$here/agents" "$claude/agents"
if [ -f "$here/instructions/AGENTS.md" ]; then
  link "$here/instructions/AGENTS.md" "$claude/CLAUDE.md"
fi

if [ "$mode" != "--uninstall" ]; then
  for ex in "$here"/skills/*/config.example.json; do
    [ -e "$ex" ] || continue
    cfg="${ex%.example.json}.json"
    if [ ! -f "$cfg" ]; then
      cp "$ex" "$cfg" && echo "created  $cfg  <- EDIT for this machine"
    fi
  done
fi
echo "done."
