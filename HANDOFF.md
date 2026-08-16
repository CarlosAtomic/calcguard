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

### 2. ~~Re-run the three unscored replay cases~~ — DONE 2026-08-16

All ten now score, deterministically: **10 pass, 0 fail, control clean**. No signal is
UNSCORED. Signals 3,4,5,6 carry REAL evidence (they fired on JR-0001/JR-0002); 1,2,7,8,9
are synthetic-only — scored and passing, never yet fired on a fork that happened.

The replay is scripted and repeatable. **Run it on every signal edit:**

```bash
curl -s http://localhost:11434/api/generate -d '{"model":"deepseek-r1:32b","prompt":"","keep_alive":"45m"}' >/dev/null
.venv/bin/python skills/engineering-judgment/acceptance/replay.py --model deepseek-r1:32b
EJ_REGRESSION=1 .venv/bin/python -m pytest tests/test_skill_acceptance.py -k regression -q
```

Takes ~15 min for the ten cases on a 32B reasoning model. Warm the model first.

### 3. ~~Watch the signal 1 / signal 4 seam~~ — RETRACTED

It does not reproduce. It came from a scorer that was sampling at temperature ~0.8
before `score()` pinned `temperature: 0`.

### 4. Signal 8 was wrong in BOTH directions — do not re-tighten it

Too broad first ("another edition is on file" — ambiently true across 4,269 PDFs), then
too narrow (a list of artefacts "you are reaching for", which excluded *comparing clause
text* and made it fail on its own fixture). The current wording covers consulting an
edition, comparison included. The reasoning is recorded in `fork-signals.md` itself.

### 5. Still open — JR-0001 on J4.3.1 needs Carlos

Unchanged from item 1 above.

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
