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
  the source is REAL     -> each Vault id resolves, and is the document claimed
  the decision is held   -> the pin resolves to a REAL test

The last one is the load-bearing check. A record whose pin names a test that
does not exist claims an enforcement it does not have, and nothing else notices:
the suite still passes, the record still LOOKS pinned, and the link is dead.
Found exactly that on JR-0002, whose pinned test had been renamed.

    python -m calcguard.judgment_lint          # every record on disk
    python -m calcguard.judgment_lint <repo>   # one repo

Or from a consuming repo's own suite, which is where it belongs -- the records
live there, and a rename should fail that repo's build, not calcguard's:

    from calcguard.judgment_lint import records, lint
    for p in records(Path(__file__).parents[1]):
        assert lint(p) == []

It lives in the PACKAGE rather than beside the skill because calcguard is
installed as a copy, not editable, so a consuming repo cannot reach the skill
directory. Stdlib only, no model calls -- it costs nothing in a normal run.
"""
from __future__ import annotations

import csv
import os
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


# The nine Vault topic codes, enumerated rather than [A-Z]{2} so that a record's
# own id (JR-0004) and a stray acronym cannot be mistaken for a catalog id.
VAULT_ID = re.compile(r"\b(?:CS|DG|EB|FR|MF|PM|RP|SA|TE)-\d{4}\b")

# A standard's designation as it is actually written beside a citation:
# S100-16, S240-20, ESR-1271, ACI 318-19. Checked against every real record --
# page ranges (`p. 155-156`) and dates (`2026-08-16`) do NOT match, because the
# trailing digit denies the word boundary.
DESIGNATION = re.compile(r"\bESR-\d{3,4}\b|\b[A-Z]{1,4}\d{2,4}-\d{2}\b|\b\d{3}-\d{2}\b")

MANIFEST_NAME = "cited-ids.csv"


def manifest_of(p: Path) -> dict[str, dict] | None:
    """`{id: row}` vendored beside the records, or None when there is none.

    Vendored rather than read from the Vault because this lint runs in consuming
    repos' suites, including CI, where no Vault is mounted. Reading the catalog
    directly would make the check pass silently everywhere it matters most.
    """
    f = p.parent / MANIFEST_NAME
    if not f.exists():
        return None
    with f.open(newline="") as fh:
        return {r["id"]: r for r in csv.DictReader(fh) if r.get("id")}


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

    # --- the cited document is real, and is the one the record claims
    #
    # The shape check above accepts `CS-0125` without asking the Vault anything,
    # so a renumbered id keeps its shape and the record keeps its green tick.
    # That is not hypothetical: CS-0726 and CS-0728 had moved to CS-0730 and
    # CS-0731, and JR-0002 and JR-0005 both linted clean pointing at nothing.
    ids = sorted(set(VAULT_ID.findall(text)))
    if ids:
        man = manifest_of(p)
        if man is None:
            bad.append(f"cites {', '.join(ids)} but {MANIFEST_NAME} is missing — run "
                       f"`python -m calcguard.judgment_lint --refresh <repo>`")
        else:
            for vid in ids:
                if vid not in man:
                    bad.append(f"{vid} is not in {MANIFEST_NAME} — renumbered, or never on "
                               f"file. Re-run --refresh; if it stays out, fix the record")
                    continue
                # The FILENAME is searched beside the title because the catalog
                # routinely carries the edition only there: CS-0528 and CS-0432
                # are both titled "Welded Box-Beam Flexure Design" and are only
                # told apart by tn-g104-14.pdf vs TechNote-G104-23SEC.pdf. On
                # title alone this check failed the two records that had been
                # most careful about which edition they cited.
                row = man[vid]
                hay = f"{row.get('title') or ''} {row.get('filename') or ''}".lower()
                for line in text.splitlines():
                    if vid not in line:
                        continue
                    # One matching designation is enough. A single line often names
                    # several sources -- GOOD's research line carries S100-16 AND
                    # ESR-1271 beside one id -- and demanding that all of them match
                    # would fail correct records for being thorough.
                    desig = DESIGNATION.findall(line)
                    if desig and not any(d.lower() in hay for d in desig):
                        bad.append(f"cites {vid} for {'/'.join(desig)}, but {vid} is "
                                   f"{row.get('title')!r} — not the document claimed")
                        break

    return bad


def refresh(root: Path) -> int:
    """Regenerate one repo's manifest from the Vault catalog.

    An id that is cited but absent from the catalog is deliberately LEFT OUT
    rather than written with a placeholder, so the next lint run fails on it.
    Writing it would launder a dead pointer into a clean tick, which is the
    exact defect this check exists to catch.
    """
    cat = Path(os.environ.get("VAULT_CATALOG", Path.home() / "Vault/_Catalog/catalog.csv"))
    if not cat.exists():
        print(f"no Vault catalog at {cat} — set VAULT_CATALOG")
        return 1
    rs = records(root)
    if not rs:
        print(f"no judgment records under {root}")
        return 1
    with cat.open(newline="") as fh:
        rows = {r["id"]: r for r in csv.DictReader(fh) if r.get("id")}
    ids = sorted({v for p in rs for v in VAULT_ID.findall(p.read_text())})
    out = rs[0].parent / MANIFEST_NAME
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "title", "filename"])
        w.writerows([i, rows[i].get("title") or "", rows[i].get("filename") or ""]
                    for i in ids if i in rows)
    missing = [i for i in ids if i not in rows]
    print(f"wrote {out} — {len(ids) - len(missing)} of {len(ids)} cited ids")
    for i in missing:
        print(f"    ✗ {i} is cited but NOT in the catalog — left out deliberately")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    do_refresh = "--refresh" in argv
    argv = [a for a in argv if a != "--refresh"]
    root = Path(argv[0]).resolve() if argv else None
    if do_refresh:
        if root is None:
            print("--refresh needs a repo path")
            return 1
        return refresh(root)
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
