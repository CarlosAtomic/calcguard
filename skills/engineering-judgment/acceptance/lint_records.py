#!/usr/bin/env python3
"""Lint judgment records — did the research actually happen?

A judgment record is a LEARNING ARTIFACT. Its value is the research it forced,
not the paperwork it produced. The engine does not guess and does not give up:
it reformulates the problem, goes to the sources, and applies existing
knowledge. Nothing here is invented.

So this checks for EVIDENCE OF THAT LOOP, not just formatting:

  research happened      -> at least one citation with an edition or section
  reformulation happened -> `judged` records enumerate candidate readings
  premises are stated    -> "What would change this" is filled in
  honesty is preserved   -> "Not covered" is filled in
  the decision is held   -> the pin resolves to a REAL test

The last one is the load-bearing check. A record whose pin names a test that
does not exist claims an enforcement it does not have, and nothing else notices:
the suite still passes, the record still LOOKS pinned, and the link is dead.
Found exactly that on JR-0002, whose pinned test had been renamed.

    python lint_records.py            # every record on disk
    python lint_records.py <repo>     # one repo

Stdlib only. No model calls, so it belongs in a normal test suite.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VERDICTS = {"determined", "judged", "insufficient_basis", "alternative_means",
            # A record whose research is done but whose code has not moved yet.
            # Legitimate -- JR-0006 used it deliberately -- but a draft is NOT
            # settled: it needs no pin and must not be cited as authority.
            "draft"}
NEEDS_PIN = {"determined", "judged", "alternative_means"}


def repo_of(p: Path) -> str:
    """The repo that OWNS this record, resolving a worktree to its main repo.

    Shared shape with replay.py:_repo_name so the two tools name a record
    identically. A worktree has `.git` as a FILE reading
    `gitdir: <main>/.git/worktrees/<name>`.
    """
    root = p.parents[2]
    g = root / ".git"
    if g.is_file():
        txt = g.read_text().strip()
        if txt.startswith("gitdir:") and "/.git/worktrees/" in txt:
            return Path(txt.split(":", 1)[1].strip().split("/.git/worktrees/")[0]).name
    return root.name


def records(root: Path | None = None) -> list[Path]:
    """Every JR-* record, de-duplicated across worktrees by slug."""
    globs = ([root.glob("docs/judgments/JR-*.md")] if root else
             [Path.home().glob("projects/*/docs/judgments/JR-*.md"),
              Path.home().glob("*/docs/judgments/JR-*.md")])
    found = [p for g in globs for p in g]
    out, seen = [], set()
    for p in sorted(found, key=lambda q: (not (q.parents[2] / ".git").is_dir(), str(q))):
        slug = re.sub(r"^JR-\d+-", "", p.stem)
        if slug not in seen:
            seen.add(slug)
            out.append(p)
    return out


def _section(text: str, title: str) -> str:
    """Body of a section, matched by TITLE not by number.

    Numbers are not stable and MUST NOT be relied on. JR-0007 inserted
    "`a` -- the undefined input" and JR-0008 inserted "What the code produced",
    shifting everything after them. An earlier version of this lint keyed on
    `## 6.` and `## 7.` and reported both records as missing three sections
    each -- two false positives on the two most thorough records in the set,
    penalising them precisely for the extra research they contained.
    """
    m = re.search(rf"^##\s*\d*\.?\s*{title}.*?$(.*?)(?=^##\s|\Z)",
                  text, re.S | re.M | re.I)
    return m.group(1).strip() if m else ""


def lint(p: Path) -> list[str]:
    """Violations for one record. Empty list means clean."""
    text = p.read_text()
    fm = text.split("---")[1] if text.startswith("---") else ""
    bad: list[str] = []

    verdict = (re.search(r"^verdict:\s*(\S+)", fm, re.M) or [None, ""])[1]
    if verdict not in VERDICTS:
        bad.append(f"verdict {verdict!r} is not one of {sorted(VERDICTS)}")

    if not re.search(r"^signals:\s*\[", fm, re.M):
        bad.append("no `signals:` declared — which signal caught this fork?")

    # --- the decision is actually held
    pin = (re.search(r"^pin:\s*(.+)$", fm, re.M) or [None, ""])[1].strip()
    if verdict in NEEDS_PIN:
        # A pin may name one test OR a whole file of them -- JR-0007 is enforced
        # by seven tests and names the file. Requiring `file::test` flagged that
        # as defective, which it is not. What must hold either way is that the
        # link is REAL and traceable BOTH ways: the target exists, and it cites
        # the record back.
        rid = (re.search(r"^id:\s*(\S+)", fm, re.M) or [None, ""])[1].strip()
        tf = p.parents[2] / (pin.split("::", 1)[0] if "::" in pin else pin)
        if not tf.exists():
            bad.append(f"pin names a path that does not exist: {tf.name}")
        else:
            src = tf.read_text()
            if "::" in pin:
                name = pin.split("::", 1)[1].strip()
                if not re.search(rf"^\s*def {re.escape(name)}\s*\(", src, re.M):
                    bad.append(f"PIN IS DEAD — {tf.name} has no `def {name}`")
            elif rid and rid not in src:
                bad.append(f"pin names a whole file, but {tf.name} never cites {rid} "
                           f"— the link is one-way and unverifiable")

    # --- evidence that the research loop ran
    # A citation SHAPE, not merely the word "edition" -- which appears in the
    # prose of every record and made this check pass on a record citing nothing.
    # Caught by its own unit test, which is the point of having one.
    if not re.search(r"§\s*\w"                 # section symbol
                     r"|\bp\.\s*\d"           # page
                     r"|\bESR-\d"              # evaluation report
                     r"|\b[A-Z]{1,4}\d{2,4}-\d{2}\b"   # S100-16, S240-20, D102-23
                     r"|\bCS-\d{4}\b", text): # vault catalog id
        bad.append("no citation shape (§, p. N, ESR-N, S100-16, CS-0125) — "
                   "was a source actually opened?")

    if verdict == "judged" and len(_section(text, "Candidate readings").split()) < 20:
        bad.append("`judged` but no candidate readings — a choice implies alternatives")

    if len(_section(text, "What would change this").split()) < 10:
        bad.append("`What would change this` is empty — the premises are not falsifiable")

    if len(_section(text, "Not covered").split()) < 10:
        bad.append("`Not covered` is empty — mandatory; it is what keeps a record honest")

    return bad


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    rs = records(root)
    if not rs:
        print("no judgment records found")
        return 0
    bad = 0
    for p in rs:
        v = lint(p)
        if v:
            bad += 1
            print(f"\n{repo_of(p)}/{p.name}")
            for x in v:
                print(f"    ✗ {x}")
        else:
            print(f"ok  {repo_of(p)}/{p.name}")
    print(f"\n{len(rs) - bad}/{len(rs)} clean")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
