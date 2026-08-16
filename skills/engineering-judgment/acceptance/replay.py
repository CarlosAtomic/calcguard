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


def real_records() -> list[tuple[Path, set[int]]]:
    """Every JR-* record on disk, with the signals it recorded."""
    out = []
    for p in sorted(Path.home().glob("projects/*/docs/judgments/JR-*.md")):
        head = p.read_text()[:800]
        if m := re.search(r"^signals: \[(.*?)\]", head, re.M):
            out.append((p, {int(n) for n in re.findall(r"\d+", m.group(1))}))
    return out


def record_forks() -> list[tuple[Path, set[int], str]]:
    """(path, recorded signals, the record's own "The fork" prose).

    Section 1 of a record is written AFTER the resolution is known, so it is
    useless for asking "can a naive reader detect this fork". It is exactly
    right for the different question this supports: do the CURRENT signal
    definitions still cover a case we already judged and pinned in code?
    """
    out = []
    for p, signals in real_records():
        if m := re.search(r"^## 1\. The fork\s*\n(.+?)(?=\n## )", p.read_text(),
                          re.M | re.S):
            out.append((p, signals, " ".join(m.group(1).split())))
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", action="append", required=True,
                    help="repeatable; disagreement between models is data")
    ap.add_argument("--seed", type=int, default=0, help="shuffle seed")
    a = ap.parse_args()

    cs = cases()
    random.Random(a.seed).shuffle(cs)          # order withheld too

    print(f"{'case':<11} {'expected':<10} " +
          " ".join(f"{m[:16]:<17}" for m in a.model))
    print("-" * (22 + 18 * len(a.model)))
    passes = fails = errs = 0
    for cid, exp, ctx in cs:
        cells, ok_all = [], True
        for m in a.model:
            got = score(m, ctx)
            if got is None:
                cells.append("ERROR"); ok_all = False; errs += 1; continue
            ok = (got == exp) if not exp else exp <= got     # control: exact
            cells.append(("+ " if ok else "! ") + str(sorted(got)))
            ok_all &= ok
        passes, fails = (passes + 1, fails) if ok_all else (passes, fails + 1)
        print(f"{cid:<11} {str(sorted(exp)):<10} " +
              " ".join(f"{c:<17}" for c in cells))

    print(f"\n{passes} pass, {fails} fail, {errs} model error(s)")
    print("A model error is NOT a pass and NOT a fail -- it is an unscored case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
