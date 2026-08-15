# calcguard — HANDOFF

**Last session:** 2026-08-15. **State:** master `1c764b4`, pushed, 43 tests passing,
tree clean.

---

## What changed this session

Added the **`engineering-judgment`** skill — a fork resolver for clause
implementation. `skills/engineering-judgment/README.md` is the full usage guide; read
that first.

**calcguard's Python package was NOT touched.** `git diff fd1f306..HEAD -- src/
pyproject.toml` is empty. `lgs-truss-designer`, `CFS_Box` and `CFS-PROFILE` all run
`calcguard 0.1.0` editable and are unaffected — nothing to reinstall.

| Added | |
|---|---|
| `skills/engineering-judgment/` | SKILL.md, README.md, 5 references, 1 asset, acceptance fixtures |
| `tests/test_skill_acceptance.py` | 4 tests, drift guard between fixtures and signal list |
| `docs/superpowers/specs/2026-08-15-engineering-judgment-design.md` | the spec |
| `docs/superpowers/plans/2026-08-15-engineering-judgment.md` | the 11-task plan |

Installed globally at `~/.claude/skills/engineering-judgment` as a **symlink** into
this repo. Master now carries `skills/`, so a `git checkout master` no longer makes the
skill vanish.

---

## RESUME — in priority order

### 1. `JR-0001` on AISI S100-16 §J4.3.1 — needs Carlos

Steps 0-5 are **done and written up** (see README's worked example). Step 6 needs two
decisions before the record can be written:

- **φ for the screw-shaft limit state.** J4.3.2 permits determining the resistance
  factor per **K2.1 (tests)** — a route the engine never engages — and the sentence
  *"shall be taken as … φ/1.25 ≥ 0.5 (LRFD)"* admits two readings that give different
  numbers. The engine's flat `PHI_SCREW = 0.50` is the conservative floor, so **no
  sealed number moves today**; what is wrong is the provenance, which currently reads
  "we used J4's φ" rather than "we declined a test-based alternative we have no data
  for". Cross-reference K2.1 has **not been opened** by lgs.
- **Where `Pnvs` comes from.** J4.3.2 gives no formula and defers to the fastener
  maker. The engine hard-codes **one** manufacturer's table (Hilti, ESR-2196/ESR-3891)
  and serves it by designation or diameter. Ladder rung 3: configuration match is a
  gate, not a preference. Mitigated — `pnvs_for_diameter` takes the **lowest**
  published value and raises rather than defaulting.

Needing no decision: interpolation reading = **Determined** (CS-0125 §J4.3.1 p. 113,
clause text explicit, `connections.py:170-172` correct). Branch selection =
**Insufficient basis**; acquisition list = **RP-0581**, **RP-0630**.

### 2. Re-run the three unscored replay cases

⛔ **Signals 2, 4, 8 and 9 have no replay evidence.** FORK-2, FORK-4 and FORK-8 went
unscored after five dispatches across two models returned no final message — a dispatch
failure, not a fixture defect. **Signal 8 is the notable gap**: it was narrowed the same
day (from "another edition is on file" to "material from a non-declared edition is in
play") and FORK-4 is its only fixture, so that narrowing is unverified.

Procedure is in the plan's Task 10. **The withholding rule is not optional** — no
Receipt column, no case id, no case count, no mention that a control exists, shuffled
order. Handed the full table an agent scores by matching clause strings.

### 3. Watch the signal 1 / signal 4 seam

The replay surfaced it: FORK-3 returned `[1,4]` against a declared `[1]`. "The clause
sends you elsewhere and I haven't gone there" is legitimately both a cross-reference
body and an unopened artifact. Harmless under "at least" scoring; worth deciding
whether the two should be disambiguated.

---

## Things that will bite you

- **Do not write the contiguous bigram `no`+`rule` in any skill file.** The prompt-injection defender matches it
  as a DAN pattern and fires HIGH severity on every read. Signal 5 was reworded for
  this. It also fires on the phrase appearing in a shell command.
- **Do not RAG a clause number.** Asking for J4.3.1 returned NFPA 13 sprinkler
  standards plus "the provided context does not contain any reference to section
  J4.3.1" — while the clause sat in CS-0125. Use `vault-sections` then `pdftotext`.
- **`llocal research` takes minutes and that is correct.** ~17 s per workspace × 16
  workspaces ÷ 4 concurrent ≈ 70 s plus merge synthesis. Warm `qwen3.6` (23 GB) first
  via `/api/generate` with `keep_alive`. A killed run is **not** an empty result.
- **The install is a symlink.** Never replace it with a copy — `reference-library`
  silently diverged that way.
- **This repo is public.** The skill files name AISI clauses and repo names, consistent
  with what the README already discloses. No client data.

## Session hygiene note

My working directory drifted to `lgs-truss-designer` during the J4.3.1 investigation
and I ran `pytest tests/` there — lgs's 2738-test suite **without** the
`OMP/OPENBLAS/MKL_NUM_THREADS=1` pins, which takes ~7 hours instead of 90 s. Killed at
2 minutes, nothing committed, lgs tree clean at `24541d0`. Use `git -C <path>` rather
than trusting cwd.
