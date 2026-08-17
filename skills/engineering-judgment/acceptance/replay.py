#!/usr/bin/env python3
"""Replay the acceptance fixtures against a local model.

The withholding rule lives HERE, in code, not in whoever runs the replay.
Each receipt in the signal table names the very clause its fixture describes --
signal 1's is "J3.4 -> Appendix A" and FORK-3's context names J3.4. Handed the
full table, a scorer matches clause strings and the suite passes for the wrong
reason. `signals_prompt_table()` strips that column; nothing else should build
the prompt.

    python replay.py --model deepseek-r1:32b
    python replay.py --model qwen3.6 --model gemma3:27b   # agreement is data

Stdlib only. Ollama on :11434.
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import re
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
FORKS = HERE / "forks.md"
SIGNALS = SKILL / "references" / "fork-signals.md"
OLLAMA = "http://localhost:11434/api/generate"

# Cases the replay has never scored. Emptied by running them -- it is not a
# list to maintain, it is a debt to pay down. Anything here is UNSCORED, never
# "passed".
UNSCORED_CASES: set[str] = set()   # all ten scored 2026-08-16 by deepseek-r1:32b


# --------------------------------------------------------------------------- parse

def _signal_rows() -> list[tuple[int, str, str]]:
    """(id, name, how-to-check) from the fork-signals table. Receipt dropped."""
    rows = []
    for line in SIGNALS.read_text().splitlines():
        if m := re.match(r"^\| (\d+) \| (.+?) \| (.+?) \| .+ \|$", line):
            rows.append((int(m.group(1)), m.group(2).strip(), m.group(3).strip()))
    return rows


def signals_prompt_table() -> str:
    """The signal table AS SHOWN TO A SCORER -- Receipt column withheld."""
    out = ["| # | Signal | How to check |", "|---|---|---|"]
    for n, name, how in _signal_rows():
        out.append(f"| {n} | {name} | {how} |")
    return "\n".join(out)


def cases() -> list[tuple[str, set[int], str]]:
    """(case id, expected signals, context prose) from forks.md."""
    text = FORKS.read_text()
    out, cid, exp = [], None, None
    for block in re.split(r"\n---\n", text):
        if not (m := re.search(r"^## ([A-Z]+-\d+)", block, re.M)):
            continue
        cid = m.group(1)
        if not (e := re.search(r"^\*\*Expected signals:\*\* (.+)$", block, re.M)):
            continue
        raw = e.group(1).strip()
        exp = set() if raw == "none" else {int(n) for n in re.findall(r"\d+", raw)}
        if c := re.search(r"^\*\*Context:\*\* (.+?)(?=\n\n|\Z)", block, re.M | re.S):
            out.append((cid, exp, " ".join(c.group(1).split())))
    return out


def _repo_name(root: Path) -> str:
    """The repo that OWNS this checkout, resolving a worktree to its main repo.

    A worktree's directory name is not its repo. `~/projects/lgs-built-up` is a
    worktree of lgs-truss-designer, and on 2026-08-17 a new worktree appearing
    moved a record key from lgs-section-designer/... to lgs-built-up/... and
    orphaned the baseline a second time. A worktree has `.git` as a FILE reading
    `gitdir: <main>/.git/worktrees/<name>`; the main repo is the part before it.
    """
    g = root / ".git"
    if g.is_file():
        txt = g.read_text().strip()
        if txt.startswith("gitdir:") and "/.git/worktrees/" in txt:
            main = txt.split(":", 1)[1].strip().split("/.git/worktrees/")[0]
            return Path(main).name
    return root.name


def record_key(p: Path) -> str:
    """Stable identity for a record: ``repo/slug``, with the JR number DROPPED.

    The number is NOT stable. On 2026-08-16 a parallel session renumbered
    JR-0001-nonsymmetric-global-buckling to JR-0003-... and every baseline key
    keyed on filename orphaned at once -- the regression then matched zero of
    twelve records and passed vacuously. The slug survived; the number did not.
    """
    slug = re.sub(r"^JR-\d+-", "", p.stem)
    return f"{_repo_name(p.parents[2])}/{slug}"


def real_records() -> list[tuple[Path, set[int]]]:
    """Every JR-* record on disk, with the signals it recorded.

    Worktrees of the same repo duplicate records; the first path wins so a
    record is not counted once per checkout.
    """
    out, seen = [], set()
    # MAIN CHECKOUTS FIRST. A worktree holds the same records under a different
    # directory name, and letting one win attributes a record to a scratch dir
    # -- which changes its key, which orphans the baseline. A main checkout has
    # `.git` as a DIRECTORY; a worktree has it as a FILE.
    found = list(Path.home().glob("projects/*/docs/judgments/JR-*.md")) + \
            list(Path.home().glob("*/docs/judgments/JR-*.md"))
    for p in sorted(found, key=lambda q: (not (q.parents[2] / ".git").is_dir(), str(q))):
        head = p.read_text()[:800]
        if not (m := re.search(r"^signals: \[(.*?)\]", head, re.M)):
            continue
        slug = re.sub(r"^JR-\d+-", "", p.stem)
        if slug in seen:
            continue
        seen.add(slug)
        out.append((p, {int(n) for n in re.findall(r"\d+", m.group(1))}))
    return out


def record_forks() -> list[tuple[Path, set[int], str]]:
    """(path, recorded signals, the record body with the answer stripped).

    The body is written AFTER the resolution is known, so it is useless for
    asking "can a naive reader detect this fork". It is exactly right for the
    different question this supports: do the CURRENT signal definitions still
    cover a case we already judged and pinned in code? For that, the scorer
    needs the evidence the original judge had.

    Frontmatter IS stripped -- it carries `signals:`, which is the answer.

    Measured 2026-08-16: feeding only section 1 does NOT work. It is a 37-48
    word QUESTION, and the evidence for signals 4 and 6 lives further down in
    Research and Not-covered. JR-0001 lost signal 4, JR-0002 lost 4 and 6.
    """
    out = []
    for p, signals in real_records():
        body = re.sub(r"\A---\n.*?\n---\n", "", p.read_text(), flags=re.S)
        out.append((p, signals, " ".join(body.split())[:6000]))
    return out


BASELINE = HERE / "record-baseline.json"


def load_baseline() -> dict[str, list[int]]:
    return json.loads(BASELINE.read_text()) if BASELINE.exists() else {}


def capture_baseline(model: str) -> dict[str, list[int]]:
    """Snapshot what THIS scorer fires on each record, right now.

    Deliberately NOT the `signals:` the record's author wrote. That field
    records what a Claude session judged; asking a different model to
    reproduce it tests whether two judges agree, which is noise. A snapshot
    holds the judge fixed so the only variable left is the signal wording --
    which is the thing a regression is supposed to be about.

    Re-capture ON PURPOSE when signals change for a reason. Never to make a
    red test green.
    """
    out = {}
    for p, _, body in record_forks():
        got, _runs = score_n(model, body)
        if got is None:
            raise RuntimeError(f"model call failed on {p.name}; refusing to "
                               f"write a baseline with a hole in it")
        out[record_key(p)] = sorted(got)
    return out


def ollama_up(timeout: int = 3) -> bool:
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=timeout)
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


# --------------------------------------------------------------------------- report

def coverage() -> dict[int, str]:
    """Per signal: REAL / SYNTHETIC-ONLY / UNSCORED. Gaps are labelled, not hidden."""
    defined = {n for n, _, _ in _signal_rows()}
    from_real = set().union(*(s for _, s in real_records())) if real_records() else set()
    scored, unscored = set(), set()
    for cid, exp, _ in cases():
        (unscored if cid in UNSCORED_CASES else scored).update(exp)
    out = {}
    for n in defined:
        if n in from_real:
            out[n] = "REAL"
        elif n in scored:
            out[n] = "SYNTHETIC-ONLY"
        else:
            out[n] = "UNSCORED"
    return out


# --------------------------------------------------------------------------- run

PROMPT = """Below are nine signals that indicate an engineering standard may not \
uniquely determine an answer during code implementation.

{table}

Some situations trip one signal, some several, and some trip none at all -- do not \
assume at least one must fire.

Judge only from the text. Reply with ONLY a JSON array of the signal numbers that \
fire, e.g. [1,4] or []. No explanation.

Situation:
{context}"""


def score(model: str, context: str, timeout: int = 600) -> set[int] | None:
    """Ask one model. None means the call failed -- never an empty set."""
    body = json.dumps({
        "model": model,
        "prompt": PROMPT.format(table=signals_prompt_table(), context=context),
        "stream": False,
        "keep_alive": "30m",
        # Greedy decoding. NECESSARY BUT NOT SUFFICIENT -- see below.
        # Without this Ollama samples at temperature ~0.8 and
        # the same fixture returns different signals run to run -- which makes
        # a snapshot fail spuriously and makes any "the fix worked" claim
        # indistinguishable from noise. Measured the hard way on 2026-08-16.
        "options": {"temperature": 0, "seed": 0, "top_p": 1.0},
        # ⚠ Reproducibility ALSO needs a quiet Ollama. Measured 2026-08-17: with a
        # second session holding deepseek-coder:32b resident alongside this model,
        # the ~900-word record bodies moved between runs while the short fixture
        # prompts did not. Concurrent requests change batch composition, which
        # changes float reduction order. Run the record regression when nothing
        # else is using :11434, and treat a failure during shared load as
        # inconclusive rather than as a signal edit.
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = json.loads(r.read())["response"]
    except (urllib.error.URLError, TimeoutError, OSError, KeyError):
        return None
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)   # reasoning models
    hits = re.findall(r"\[[\d,\s]*\]", text)
    if not hits:
        return None
    return {int(n) for n in re.findall(r"\d+", hits[-1])}


RUNS = 5


def score_n(model: str, context: str, n: int = RUNS
            ) -> tuple[set[int] | None, list[set[int]]]:
    """Run n times; a signal fires if it appears in a MAJORITY of runs.

    ONE DRAW IS A SAMPLE, NOT A MEASUREMENT. Measured 2026-08-17 on an idle
    machine: the same short fixture returned [4] and then [4,8] on consecutive
    calls with temperature 0, seed 0. Ollama is not bitwise deterministic on
    GPU -- non-associative float reduction is enough to flip a borderline
    token, and a borderline token flips a signal.

    Three agreeing draws is not proof either. I generalised from n=3, called
    the replay deterministic, and reported a 10/10 that was a single sample.

    Aggregation is PER SIGNAL, not per result set: exact sets rarely tie, while
    "does signal 8 fire more often than not" is the question actually being
    asked.
    """
    runs: list[set[int]] = []
    for _ in range(n):
        got = score(model, context)
        if got is None:
            return None, runs
        runs.append(got)
    need = n // 2 + 1
    counts = collections.Counter(s for r in runs for s in r)
    return {s for s, c in counts.items() if c >= need}, runs


def freq(runs: list[set[int]]) -> str:
    """`4:5 8:3` -- how many of the runs each signal appeared in."""
    c = collections.Counter(s for r in runs for s in r)
    return " ".join(f"{s}:{n}" for s, n in sorted(c.items())) or "-"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", action="append", required=True,
                    help="repeatable; disagreement between models is data")
    ap.add_argument("--seed", type=int, default=0, help="shuffle seed")
    ap.add_argument("--runs", type=int, default=RUNS,
                    help="samples per case; a signal fires on a MAJORITY. "
                         "One draw is a sample, not a measurement.")
    ap.add_argument("--capture-baseline", action="store_true",
                    help="snapshot what fires on each JR record; do this ON PURPOSE")
    a = ap.parse_args()

    if a.capture_baseline:
        snap = capture_baseline(a.model[0])
        BASELINE.write_text(json.dumps(snap, indent=2) + "\n")
        print(f"baseline written to {BASELINE.name} using {a.model[0]}:")
        for k, v in snap.items():
            print(f"  {k}: {v}")
        return 0

    cs = cases()
    random.Random(a.seed).shuffle(cs)          # order withheld too

    print(f"{a.runs} runs per case; a signal fires on a majority "
          f"(>={a.runs // 2 + 1}/{a.runs}). Parenthesised = signal:hits.\n")
    print(f"{'case':<11} {'expected':<10} " +
          " ".join(f"{m[:16]:<34}" for m in a.model))
    print("-" * (22 + 35 * len(a.model)))
    passes = fails = errs = 0
    for cid, exp, ctx in cs:
        cells, ok_all = [], True
        for m in a.model:
            got, runs = score_n(m, ctx, a.runs)
            if got is None:
                cells.append("ERROR"); ok_all = False; errs += 1; continue
            ok = (got == exp) if not exp else exp <= got     # control: exact
            cells.append(("+ " if ok else "! ") + f"{sorted(got)} ({freq(runs)})")
            ok_all &= ok
        passes, fails = (passes + 1, fails) if ok_all else (passes, fails + 1)
        print(f"{cid:<11} {str(sorted(exp)):<10} " +
              " ".join(f"{c:<34}" for c in cells))

    print(f"\n{passes} pass, {fails} fail, {errs} model error(s)")
    print("A model error is NOT a pass and NOT a fail -- it is an unscored case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
