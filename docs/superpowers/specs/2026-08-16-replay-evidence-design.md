# Trustworthy replay evidence — design

**Status:** spec, 2026-08-16. **Scope:** ~60 lines of Python, one new test.
**Prior:** `2026-08-15-engineering-judgment-design.md`.

This spec is deliberately short. The last one ran 286 lines and its plan 1321, to
produce 872 lines of markdown — a Karpathy audit called the scaffolding heavier than
the artifact, and it was right. Scale the process to the work.

## Problem

The acceptance suite reports 6 of 9 scored cases passing and a clean control. That
sounds like evidence and mostly is not:

- **Signals 2, 4, 8 and 9 were never scored.** Subagent dispatch dropped the same three
  cases five times across two models. Unscored, not passed.
- **Signal 8's narrowing is unverified.** It was broadened and then narrowed on the same
  day; FORK-4 is its only fixture and FORK-4 is one of the three that never ran.
- **The replay is not repeatable.** It cost tokens, ran once, and cannot be re-run when
  a signal changes — which is precisely when the evidence goes stale.
- **Two real records now exist** (`lgs-section-designer` JR-0001, JR-0002) and nothing
  checks that editing a signal leaves them still supported.

## What we build

### A. Honest coverage labelling

`acceptance/forks.md` gains a real-record tier that **references records by path, not by
copy**, so a record edit cannot silently drift from its fixture.

One new test reports per signal: `REAL` / `SYNTHETIC-ONLY` / `UNSCORED`. It does not
fail on a gap — it makes the gap visible. A suite that implies uniform confidence it
does not have is worse than one that admits the hole.

### B. Scripted local replay — the routine gate

`skills/engineering-judgment/acceptance/replay.py`.

- Parses `forks.md`, **builds the withheld prompt in code**: strips the Receipt column,
  drops case ids, shuffles order. The withholding rule stops depending on whoever runs
  it remembering to apply it.
- POSTs each case to `http://localhost:11434/api/generate`, parses the JSON array.
- `--model` repeatable, so `deepseek-r1:32b`, `qwen3.6`, `gemma3:27b` can be compared.
  **Disagreement between models is data**: a signal only one model detects is weak.
- Writes a table to stdout; the replay log in `forks.md` is updated by hand from it.

Repeatable, free, and re-runnable on every signal edit.

### C. Real-record regression

For each `JR-*.md` under `~/projects/*/docs/judgments/`, replay its **§1 The fork** and
assert the recorded `signals:` still fire.

The question here is different from the acceptance suite's, and the difference is the
whole justification. §1 is written *after* the resolution is known, so it is useless for
asking "can a naive reader detect this fork." It is exactly right for asking **"do the
current signal definitions still cover a case we already judged and pinned in code?"**
Edit signal 3 and this says whether JR-0001 and JR-0002 just became unsupported.

Skipped cleanly when Ollama is unreachable — never a false green.

### D. Claude spot check

Stays manual and documented. The skill runs under Claude; a local model is a proxy.
Not automated, not on every change.

## Out of scope

- Pruning or merging signals. Signal 7 has never fired in production but its receipt is
  a real 1.43× defect that predates the skill. "Unexercised" is not "unneeded", and
  n = 2 is far too thin to cut on.
- Changing any signal's wording. This iteration changes what we *know*, not what the
  skill *does*.
- Replacing the synthetic fixtures. They stay; the real ones are added beside them.

## Done when

1. `replay.py --model deepseek-r1:32b` scores all 10 cases, **including the three that
   never ran**, and prints a table.
2. The coverage test prints a per-signal label and the suite stays green.
3. The regression check passes for JR-0001 and JR-0002, and **is shown to fail** when a
   signal they depend on is mutated.
4. `forks.md`'s replay log records real numbers, with any remaining gap still named.

Criterion 3 is the one that matters. A regression check never observed failing is an
alibi, not a guard.
