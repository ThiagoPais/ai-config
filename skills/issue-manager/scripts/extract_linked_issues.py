#!/usr/bin/env python3
"""Extract GitHub closing-keyword issue references from PR title/body text.

Finds occurrences of GitHub's own "closes/fixes/resolves" syntax so you don't
have to hand-write this regex every time:
  - close, closes, closed / fix, fixes, fixed / resolve, resolves, resolved
  - followed by "#123", "owner/repo#123", or a full issue URL

Usage:
  python3 extract_linked_issues.py <file>
  cat pr_body.txt | python3 extract_linked_issues.py -

Prints one reference per line, e.g.:
  123
  some-owner/other-repo#456

No output means no closing-keyword references were found in the text — that's
a real, useful signal (ask the user which issue this targets), not an error.
"""
import re
import sys

_CLOSING_KEYWORDS = r"(?:clos(?:e|es|ed)|fix(?:es|ed)?|resolv(?:e|es|ed))"

_PATTERN = re.compile(
    rf"\b{_CLOSING_KEYWORDS}\s*:?\s*"
    r"(?:(?P<owner_repo>[\w.-]+/[\w.-]+)#(?P<num1>\d+)"
    r"|#(?P<num2>\d+)"
    r"|https?://github\.com/(?P<url_owner_repo>[\w.-]+/[\w.-]+)/issues/(?P<num3>\d+))",
    re.IGNORECASE,
)


def extract(text: str) -> list[str]:
    refs = []
    for m in _PATTERN.finditer(text):
        if m.group("num1"):
            refs.append(f'{m.group("owner_repo")}#{m.group("num1")}')
        elif m.group("num2"):
            refs.append(m.group("num2"))
        elif m.group("num3"):
            refs.append(f'{m.group("url_owner_repo")}#{m.group("num3")}')
    return refs


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    source = sys.argv[1]
    text = sys.stdin.read() if source == "-" else open(source, encoding="utf-8").read()

    for ref in extract(text):
        print(ref)


if __name__ == "__main__":
    main()
