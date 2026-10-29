#!/usr/bin/env python3
"""docs-lint: deterministic conformance checks for project documentation.

Implements the mechanical half of CONVENTIONS.md (structure, naming, frontmatter,
required sections, ADR integrity, links, requirement IDs). Judgment checks
(leakage, duplication, contradictions) are done by the docs-auditor agent.

Python 3.8+, standard library only.

Usage:
  docs-lint.py [PROJECT ...] [--docs-root PATH] [--json] [--min-severity LEVEL]
               [--changed] [--strict]
  docs-lint.py --print-root | --print-context [--docs-root PATH]

Exit code: 1 when any error exists (or any warning with --strict), else 0.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
DEFAULTS = {"docs_root": "", "reserved_dirs": ["templates", "guides", "tooling", "node_modules"], "stale_days": 180}


def load_config() -> dict:
    """Per-machine settings from ../config.json (git-ignored; see config.example.json)."""
    cfg = dict(DEFAULTS)
    try:
        cfg.update(json.loads(CONFIG_PATH.read_text()))
    except (OSError, ValueError):
        pass
    return cfg


CONFIG = load_config()
RESERVED = set(CONFIG["reserved_dirs"])
STD_DIRS = {"adr", "features", "infra", "proposal", "assets"}
ARTIFACT_EXT = (".aux", ".log", ".fls", ".fdb_latexmk", ".synctex.gz", ".out", ".toc", ".bbl", ".blg")
DOC_STATUS = {"draft", "active", "archived"}
ADR_STATUS = {"proposed", "accepted", "rejected", "deprecated", "superseded"}
STALE_DAYS = int(CONFIG["stale_days"])
SEVERITY_ORDER = {"info": 0, "warn": 1, "error": 2}
DB_WORDS = re.compile(r"\b(database|postgres(?:ql)?|mysql|mongodb|prisma|supabase|sql|schema)\b", re.I)
REQ_RE = re.compile(r"\b(?:FR|NFR)-\d{1,3}\b")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


# ---------------------------------------------------------------- context ---

def _read_pointer(path: Path) -> dict:
    out = {}
    try:
        lines = [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]
    except OSError:
        return out
    for i, line in enumerate(lines):
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
        elif i == 0:
            out["root"] = line
    return out


def resolve_context(explicit: str | None = None, start: Path | None = None) -> dict | None:
    """Locate the docs repo. Order: explicit path, cwd/parents marker, .docs-root, DOCS_ROOT env var, config.json."""
    start = (start or Path.cwd()).resolve()

    def ctx(root: Path, source: str, project: str | None = None, mode: str = "docs-repo") -> dict:
        root = root.resolve()
        if project is None and start != root:
            try:
                first = start.relative_to(root).parts[0]
                if first not in RESERVED and not first.startswith("."):
                    project = first
            except (ValueError, IndexError):
                pass
        return {"root": str(root), "project": project, "source": source, "mode": mode, "cwd": str(start)}

    if explicit:
        p = Path(explicit).expanduser().resolve()
        return ctx(p, "argument") if (p / "CONVENTIONS.md").exists() else None
    for d in [start, *start.parents]:
        if (d / "CONVENTIONS.md").exists():
            return ctx(d, "cwd")
        ptr = d / ".docs-root"
        if ptr.is_file():
            info = _read_pointer(ptr)
            p = Path(info.get("root", "")).expanduser()
            if (p / "CONVENTIONS.md").exists():
                return ctx(p, f"{ptr}", info.get("project"), "code-repo")
    env = os.environ.get("DOCS_ROOT")
    if env and (Path(env).expanduser() / "CONVENTIONS.md").exists():
        return ctx(Path(env).expanduser(), "DOCS_ROOT", None, "code-repo")
    cfg_root = CONFIG.get("docs_root")
    if cfg_root and (Path(cfg_root).expanduser() / "CONVENTIONS.md").exists():
        return ctx(Path(cfg_root).expanduser(), str(CONFIG_PATH), None, "code-repo")
    return None


# ---------------------------------------------------------------- parsing ---

def split_frontmatter(text: str):
    m = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?", text, re.S)
    if not m:
        return None, text
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("'\"")
    return fm, text[m.end():]


def strip_code(text: str) -> str:
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", "", text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", text)


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def norm_heading(h: str) -> str:
    h = strip_comments(h)
    h = re.sub(r"^\s*\d+(?:\.\d+)*\.?\s*", "", h)
    h = re.sub(r"[^a-z0-9]+", " ", h.lower())
    return h.strip()


def doc_headings(body: str) -> list[str]:
    text = strip_comments(strip_code(body))
    return [norm_heading(m.group(2)) for m in re.finditer(r"^(#{2,6})[ \t]+(.+?)[ \t#]*$", text, re.M)]


def template_required(root: Path, ttype: str) -> list[str]:
    p = root / "templates" / f"{ttype}.md"
    if not p.is_file():
        return []
    _, body = split_frontmatter(p.read_text())
    body = strip_code(body)
    req = []
    for line in body.splitlines():
        m = re.match(r"^##[ \t]+(.+)$", line)
        if m and "<!-- optional -->" not in m.group(1):
            req.append(norm_heading(m.group(1)))
    return req


def md_links(body: str) -> list[str]:
    text = strip_comments(strip_code(body))
    return re.findall(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", text)


# ----------------------------------------------------------------- linter ---

class Linter:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[dict] = []
        self.req_cache: dict[str, list[str]] = {}

    def add(self, sev: str, code: str, path: Path | str, msg: str, hint: str = ""):
        try:
            rel = str(Path(path).relative_to(self.root))
        except ValueError:
            rel = str(path)
        self.findings.append({"severity": sev, "code": code, "path": rel, "message": msg, "hint": hint})

    def required(self, ttype: str) -> list[str]:
        if ttype not in self.req_cache:
            self.req_cache[ttype] = template_required(self.root, ttype)
        return self.req_cache[ttype]

    # -- helpers
    @staticmethod
    def classify(rel: Path, name: str) -> str | None:
        s = rel.as_posix()
        table = {
            f"{name}.md": "overview", f"{name}-prd.md": "prd", f"{name}-dbdd.md": "dbdd",
            f"{name}-roadmap.md": "roadmap", f"{name}-glossary.md": "glossary",
            f"infra/{name}-ops.md": "ops", "adr/README.md": "adr-index",
        }
        if s in table:
            return table[s]
        if re.match(r"^adr/\d{3}-[a-z0-9-]+\.md$", s):
            return "adr"
        if s.startswith("features/"):
            return "feature"
        return None

    # -- per project
    def lint_project(self, name: str):
        base = self.root / name
        if not KEBAB_RE.match(name):
            self.add("warn", "bad-project-name", name, f"Project folder '{name}' is not kebab-case.")

        files = [p for p in base.rglob("*") if p.is_file() and not any(part.startswith(".") for part in p.relative_to(base).parts)]
        rels = {p: p.relative_to(base) for p in files}
        text_of: dict[Path, str] = {}
        for p in files:
            if p.suffix == ".md":
                try:
                    text_of[p] = p.read_text(errors="replace")
                except OSError:
                    pass

        # expected documents
        expected = {
            "overview": (base / f"{name}.md", "error"),
            "prd": (base / f"{name}-prd.md", "error"),
            "roadmap": (base / f"{name}-roadmap.md", "warn"),
            "glossary": (base / f"{name}-glossary.md", "info"),
            "ops": (base / "infra" / f"{name}-ops.md", "info"),
        }
        mentions_db = any(
            DB_WORDS.search(text_of.get(expected[k][0], "")) for k in ("overview", "prd")
        )
        expected["dbdd"] = (base / f"{name}-dbdd.md", "warn" if mentions_db else "info")
        for t, (path, sev) in expected.items():
            if not path.exists():
                self.add(sev, "missing-doc", base, f"Missing {t} document: expected {path.relative_to(self.root)}.",
                         f"Create from templates/{t}.md (docs-init or docs-author).")

        # stray files / dirs at project root
        std_names = {p.name for p, _ in [expected[k] for k in expected]}
        for child in sorted(base.iterdir()):
            if child.name.startswith("."):
                continue
            if child.is_dir():
                if child.name not in STD_DIRS:
                    self.add("warn", "nonstandard-dir", child, f"Folder '{child.name}/' is not part of the standard layout.",
                             "Rename/move: proposal sources -> proposal/, diagrams -> assets/, scripts and CI refs -> infra/.")
            elif child.name not in std_names:
                self.add("warn", "stray-file", child, f"File '{child.name}' is not a standard project document.",
                         "Move CI/scripts to infra/, fold or rename documents to the standard names.")

        # build artifacts (aggregated)
        arts = [p for p in files if p.name.endswith(ARTIFACT_EXT)]
        if arts:
            ex = ", ".join(str(rels[p]) for p in arts[:3])
            self.add("warn", "build-artifact", base, f"{len(arts)} build artifact(s) committed (e.g. {ex}).",
                     "Add them to .gitignore and git rm --cached; keep sources and the final PDF.")

        # per-document checks
        defined_ids: set[str] = set()
        prd_path = expected["prd"][0]
        if prd_path in text_of:
            defined_ids = set(REQ_RE.findall(strip_code(text_of[prd_path])))
            if not defined_ids:
                self.add("warn", "prd-no-requirement-ids", prd_path, "PRD defines no FR-/NFR- requirement IDs.",
                         "Give each requirement a stable ID (see guides/prd.md).")

        adr_numbers: dict[int, Path] = {}
        adr_fm: dict[int, dict] = {}

        for p, text in text_of.items():
            rel = rels[p]
            ttype = self.classify(rel, name)

            # links (all md)
            for target in md_links(text):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                    continue
                t = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not t:
                    continue
                dest = (p.parent / t).resolve() if not t.startswith("/") else Path(t)
                if not dest.exists():
                    self.add("error", "broken-link", p, f"Broken relative link: {target}", "Fix the path or remove the link.")

            # requirement refs outside the PRD
            if prd_path in text_of and p != prd_path:
                body_nc = strip_code(text)
                missing = sorted(set(REQ_RE.findall(body_nc)) - defined_ids)
                if missing and (ttype is not None):
                    self.add("error", "undefined-requirement", p,
                             f"References requirement(s) not defined in the PRD: {', '.join(missing)}.",
                             "Define them in the PRD or fix the reference.")

            if ttype in (None, "feature"):
                continue

            fm, body = split_frontmatter(text)
            if fm is None:
                self.add("warn", "missing-frontmatter", p, "No frontmatter block.",
                         f"Add type/project/status/updated (type: {ttype}).")
            else:
                self.check_frontmatter(p, fm, ttype, name)

            req = self.required(ttype)
            if req:
                have = doc_headings(body)
                missing_sec = [r for r in req if not any(r in h for h in have)]
                if missing_sec:
                    self.add("warn", "missing-section", p, f"Missing required section(s): {', '.join(missing_sec)}.",
                             f"See templates/{ttype}.md and guides/{ttype}.md.")

            if ttype == "overview" and "github.com/" not in text:
                self.add("warn", "missing-repo-link", p, "Overview has no GitHub repository URL.",
                         "Add a Repositories table with the code repo URLs.")

            if ttype == "adr":
                m = re.match(r"^adr/(\d{3})-", rel.as_posix())
                num = int(m.group(1))
                if num in adr_numbers:
                    self.add("error", "adr-duplicate-number", p, f"ADR number {num:03d} is also used by {adr_numbers[num].name}.")
                adr_numbers[num] = p
                adr_fm[num] = fm or {}
                if fm and fm.get("number") and fm["number"].lstrip("0") != str(num):
                    self.add("error", "adr-number-mismatch", p, f"Frontmatter number '{fm['number']}' does not match filename ({num:03d}).")

        # ADR set checks
        if adr_numbers:
            for n in range(1, max(adr_numbers) + 1):
                if n not in adr_numbers:
                    self.add("warn", "adr-gap", base / "adr", f"ADR numbering gap: {n:03d} is missing.",
                             "Numbers are never reused; restore the file or accept the gap and mark it in the index.")
            if not (base / "adr" / "README.md").exists():
                self.add("warn", "missing-adr-index", base / "adr", "adr/ has no README.md index.", "Create from templates/adr-index.md.")
            for num, fm in adr_fm.items():
                p = adr_numbers[num]
                sup_by = re.sub(r"\D", "", fm.get("superseded-by", "") or "")[:3]
                status = fm.get("status", "")
                if sup_by:
                    t = int(sup_by)
                    if status != "superseded":
                        self.add("error", "adr-status-mismatch", p, f"superseded-by is set but status is '{status}'.")
                    if t not in adr_numbers:
                        self.add("error", "adr-broken-supersede", p, f"superseded-by points to missing ADR {t:03d}.")
                    else:
                        back = re.findall(r"\d{3}", adr_fm[t].get("supersedes", "") or "")
                        if f"{num:03d}" not in back:
                            self.add("warn", "adr-supersede-not-reciprocal", adr_numbers[t],
                                     f"ADR {num:03d} says it is superseded by {t:03d}, but {t:03d} does not list 'supersedes: {num:03d}'.")
                elif status == "superseded":
                    self.add("error", "adr-status-mismatch", p, "status is 'superseded' but superseded-by is not set.")

    def check_frontmatter(self, p: Path, fm: dict, ttype: str, project: str):
        if fm.get("type") != ttype:
            self.add("error", "type-mismatch", p, f"Frontmatter type '{fm.get('type', '')}' does not match expected '{ttype}'.")
        if fm.get("project") != project:
            self.add("error", "project-mismatch", p, f"Frontmatter project '{fm.get('project', '')}' does not match folder '{project}'.")
        valid = ADR_STATUS if ttype == "adr" else DOC_STATUS
        status = fm.get("status", "")
        if status not in valid:
            self.add("error", "invalid-status", p, f"Invalid status '{status}' for {ttype}; allowed: {', '.join(sorted(valid))}.")
        upd = fm.get("updated", "")
        try:
            d = dt.date.fromisoformat(upd)
            if status in ("active", "accepted") and (dt.date.today() - d).days > STALE_DAYS and ttype in ("overview", "roadmap", "ops"):
                self.add("info", "stale", p, f"Not updated in {(dt.date.today() - d).days} days.", "Review and bump 'updated', or archive.")
        except ValueError:
            self.add("error", "invalid-updated", p, f"'updated' must be YYYY-MM-DD, got '{upd}'.")
        if ttype == "adr" and not fm.get("number"):
            self.add("error", "adr-missing-number", p, "ADR frontmatter has no 'number'.")


def list_projects(root: Path) -> list[str]:
    return sorted(
        d.name for d in root.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name not in RESERVED
    )


def changed_projects(root: Path) -> list[str]:
    try:
        out = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    names = set()
    for line in out.splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ")[-1]
        first = path.split("/", 1)[0]
        if "/" in path and first not in RESERVED and not first.startswith("."):
            names.add(first)
    return sorted(names)


# -------------------------------------------------------------------- cli ---

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="*", help="Project folder names (default: all).")
    ap.add_argument("--docs-root", help="Path to the docs repo (contains CONVENTIONS.md).")
    ap.add_argument("--json", action="store_true", help="Machine-readable output.")
    ap.add_argument("--min-severity", choices=list(SEVERITY_ORDER), default="info")
    ap.add_argument("--changed", action="store_true", help="Only projects with uncommitted changes.")
    ap.add_argument("--strict", action="store_true", help="Exit 1 on warnings too.")
    ap.add_argument("--print-root", action="store_true", help="Print the resolved docs root and exit.")
    ap.add_argument("--print-context", action="store_true", help="Print resolved context as JSON and exit.")
    a = ap.parse_args(argv)

    ctx = resolve_context(a.docs_root)
    if a.print_root or a.print_context:
        if not ctx:
            print("Docs repo not found. Pass --docs-root, run inside it, set DOCS_ROOT, set docs_root in the skill's config.json, or add a .docs-root file.", file=sys.stderr)
            return 2
        print(json.dumps(ctx) if a.print_context else ctx["root"])
        return 0
    if not ctx:
        print("Docs repo not found. Pass --docs-root, run inside it, set DOCS_ROOT, set docs_root in the skill's config.json, or add a .docs-root file.", file=sys.stderr)
        return 2

    root = Path(ctx["root"])
    projects = a.projects or ([ctx["project"]] if ctx.get("project") and ctx["mode"] == "code-repo" else [])
    if a.changed:
        projects = changed_projects(root)
    if not projects:
        projects = list_projects(root)
    unknown = [p for p in projects if not (root / p).is_dir()]
    if unknown:
        print(f"Unknown project(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    lint = Linter(root)
    for p in projects:
        lint.lint_project(p)

    # root README must mention each project
    readme = root / "README.md"
    if readme.exists() and not a.projects:
        rt = readme.read_text(errors="replace")
        for p in projects:
            if f"{p}/" not in rt:
                lint.add("warn", "project-not-in-readme", readme, f"Root README does not list project '{p}'.")

    min_level = SEVERITY_ORDER[a.min_severity]
    findings = [f for f in lint.findings if SEVERITY_ORDER[f["severity"]] >= min_level]
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f["severity"]], f["path"], f["code"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("error", "warn", "info")}

    if a.json:
        print(json.dumps({"root": str(root), "projects": projects, "counts": counts, "findings": findings}, indent=2))
    else:
        print(f"docs-lint · root: {root} · projects: {', '.join(projects)}")
        for sev in ("error", "warn", "info"):
            group = [f for f in findings if f["severity"] == sev]
            if not group:
                continue
            print(f"\n{sev.upper()} ({len(group)})")
            for f in group:
                print(f"  [{f['code']}] {f['path']}\n      {f['message']}" + (f"\n      -> {f['hint']}" if f["hint"] else ""))
        print(f"\nSummary: {counts['error']} error(s), {counts['warn']} warning(s), {counts['info']} info")

    fail = counts["error"] > 0 or (a.strict and counts["warn"] > 0)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
