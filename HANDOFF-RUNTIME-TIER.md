# HANDOFF — the runtime tier, and whether calcguard should have one

**Started:** 2026-08-19 · **Status:** ✅ **KEPT and MERGED 2026-08-21** (Carlos) — still used by nothing
**Branch:** `feat/runtime-tier` → merged to master at `e27a240`, pushed. 68 tests green
**Commit:** `373f04b` — `require_within`, 6 tests, suite 61 passed / 1 skipped

---

## Read this first: the branch exists because of a premise that turned out false

The task was *"promote calcguard from tests into the engine"* — recommendation #1 of an
audit into what would reduce error in the AISI/ASCE work. Two discoveries killed that
premise, in order:

1. **calcguard's assertions cannot run in an engine.** `CalcGuardError` subclasses
   `AssertionError` *by design* — its own docstring says so, to make pytest report a
   failure rather than an error. In a shipped engine that is wrong: callers catch
   `ValueError`, an `AssertionError` reaching an API is a crash rather than a refusal,
   and `python -O` strips asserts. Several assertions (`assert_scales`,
   `assert_monotonic`) also probe a *function* across many inputs, which a solver cannot
   do inline.

2. **So this branch added a runtime tier** — `require_within`, which refuses unless
   `lo <= value <= hi` and raises **an exception type the caller supplies**, so an engine
   keeps its own refusal vocabulary. Both bounds required; non-finite refused before the
   comparison.

3. **Then the next decision made it moot.** calcguard is a **dev-only** dependency in
   every consumer (verified below). Importing it in `lgs/src/cfs_truss/buckling.py` would
   fail every production install with an ImportError on the engine's core module. Carlos
   chose **native implementation**, which was correct — and left `require_within` with no
   caller.

**The invariants shipped natively instead.** lgs master now carries four runtime physics
guards (`b50d42c`, CI green 31.2 min), none of which import calcguard.

---

## The actual state, measured 2026-08-19

| consumer | calcguard in test files | in engine source | pyproject group |
|---|---|---|---|
| lgs-truss-designer | 16 | **0** | dev |
| CFS-PROFILE | 10 | **0** | dev |
| lgs-wind-case-b | 5 | **0** | dev |
| CFS_Box | 2 | **0** | dev |

**Every consumer treats calcguard as dev-only, and none imports it from engine source.**
That is not an oversight in three of them and a decision in one — it is uniform.

---

## The question this branch is waiting on

**Should calcguard have a runtime tier at all?**

**Case for parking it (delete the branch, or leave it unmerged):**
- No consumer can use it without promoting calcguard to a production dependency, which
  means a **git-pinned GitHub repo in every deploy path**. lgs's own `pyproject.toml`
  carries a comment recording that a stale pin once aborted an entire pytest run at
  collection — zero tests executed, and both versions self-report `0.1.0`, so `pip show`
  could not tell them apart.
- The native guards in lgs are ~10 lines each and read better at the site they protect.
- Merging unused code to master is worse than parking it.

**Case for keeping it:**
- `require_within` is sound, tested, and the *discipline* it encodes — both bounds
  required, non-finite refused first, caller-supplied error type — is worth having
  written down once rather than re-derived per repo.
- If any consumer ever does accept calcguard as a production dependency, this is what it
  would need.
- It costs nothing to leave on a branch.

**Not yet investigated:** whether CFS_Box or CFS-PROFILE would tolerate calcguard as a
production dependency. Both are dev-only today, but neither has lgs's deploy constraints
and neither was asked. That is the one open fact that could change the answer.

---

## If the answer is "keep it", what would need to happen

1. Pick a consumer that accepts a production dependency on calcguard.
2. **Push calcguard and move the pin in the SAME commit** as any consumer code needing
   it. lgs's pyproject records why: a test was added importing `calcguard.judgment_lint`
   without moving the pin, and a fresh install got a calcguard without the module, which
   raised at collection and aborted the whole run.
3. Verify a clean-room install: `pip install .` **without** dev extras, then import the
   engine module. That is the check that would have caught the ImportError.

## ~~If the answer is "park it"~~ — not taken

---

## Verify criteria

- A decision is recorded here, either way. ✅ **KEEP — Carlos, 2026-08-21.** Merged on the
  discipline `require_within` encodes (both bounds required, non-finite refused first,
  caller-supplied error type) rather than on present usage.
- If kept: one real consumer imports `require_within` from engine source, and a
  no-dev-extras install of that consumer still imports. ❌ **STILL OPEN — this is the
  live risk.** Merging did not create a caller. calcguard remains dev-only in all four
  consumers, so importing it from engine source would still fail a production install.
  Whoever picks this up: pick the consumer FIRST, and move its pin in the SAME commit.
- If parked: the branch is registered wherever this repo tracks parked work. ❌ open
