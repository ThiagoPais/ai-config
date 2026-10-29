# ~/.agents

Personal AI tooling: skills, agents and global instructions, shared across my computers.

```
skills/         skills (own + installed via the skills CLI; see .skill-lock.json)
agents/         subagent definitions (flat .md files)
instructions/   AGENTS.md (the tool-neutral main file), linked into each tool's config folder
install.sh      symlinks everything into ~/.claude and creates config.json files
```

## New machine

```bash
git clone <remote> ~/.agents
~/.agents/install.sh
```

Then edit each generated `skills/*/config.json` (git-ignored). Example: `skills/docs-audit/config.json` -> `docs_root`.

## Rules

- No absolute paths, usernames or hostnames inside skills/agents. Per-machine values go in `config.json` next to the skill, with a committed `config.example.json`.
- Agents are single files, so they receive their paths as inputs from the skill that calls them.
