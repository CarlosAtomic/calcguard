# calcguard — HANDOFF

**Updated:** 2026-08-18. **calcguard master `cd706ea`**, pushed, 55 passed / 1 skipped.

---

## What the final product is

**A documented basis for trusting the engineering software Carlos writes to replace paid
tools.** That is the objective. What paid software really sells is not its arithmetic —
it is the assurance behind it. This repo is that assurance, made executable.

Three parts, answering three different questions:

| Part | Question | Form |
|---|---|---|
| **calcguard** | *Does this structure obey physics?* | executable assertions — equilibrium, sign, scaling, closed form, coverage |
| **engineering-judgment** | *Was that the right clause, edition and reading?* | a Claude Code skill that fires only at a fork |
| **judgment records** | *Why was it decided that way, and is it still true?* | `docs/judgments/JR-NNNN-*.md` in the consuming repo, each pinned by a test |

**calcguard and engineering-judgment never exchange data.** One asserts numbers, the
other decides which clause produces them. Conflating those was the original design
error; separating them is the design.

The third row is the output that compounds. A fork resolved once becomes retrievable by
every later project instead of being re-litigated.

---

## Accomplished

### The skill — built, shipped, in production use

`~/.claude/skills/engineering-judgment` → **symlinked** into this repo, so the installed
copy cannot silently diverge the way `reference-library` once did. Global; nothing to
install per project. calcguard's Python package is untouched — `src/` and
`pyproject.toml` are byte-identical, so `lgs-truss-designer`, `CFS_Box` and `CFS-PROFILE`
are unaffected.

- **9 enumerated fork signals**, each derived from a defect that actually happened
- Fires **only** on a signal — an unambiguous clause costs nothing, by design
- Basis read from `code-basis.toml`; never interrogates for permit dates
- Research order: `vault-sections` → `vault-search --json` → the clause PDF → the
  `reference-library` gate
- Four verdicts: **Determined / Judged / Insufficient basis / Alternative means**
- `decided_by: Carlos` — the skill never decides

### It is being used

**11 judgment records exist** (`JR-0001` … `JR-0011`) across `lgs-truss-designer` and
`lgs-section-designer` — screw shaft shear, `Pnvs` across manufacturers, nonsymmetric
global buckling, axis selection, built-up pairs, web crippling and more. Each is pinned
by a test whose docstring cites it.

**All 9 signals now carry REAL evidence.** Signal 7 (cross-table pairing) was the last
synthetic-only one and has since fired on real work. Nothing is unexercised.

### Verification that actually verifies

- **Scripted local replay** — `acceptance/replay.py`, stdlib only, model-agnostic
- **The withholding rule lives in code**: Receipt column stripped, case ids dropped,
  order shuffled. It cannot be forgotten by whoever runs it
- **5 runs per case, majority ≥3/5**, per-signal frequencies printed
- **Result: 10 pass, 0 fail. `CONTROL-1` fired nothing in any run**
- **Record regression** compares against `record-baseline.json`, a snapshot taken with
  the *same* scorer — passes across all records, and **verified firing** when a signal is
  mutated
- Drift guard in the pytest suite; coverage labelled per signal, never assumed

### Defects found and fixed

| Found | Fix |
|---|---|
| `connection_check` never applied J4.3.2 — the screw could not govern | wired `pnvs` through; merged `4bb82e8` |
| Signal 8 fired on *every* clause (a second edition on file is ambiently true) | narrowed to material actually in play |
| …then failed to fire on its own fixture | reworded again to include comparing clause text |
| Fixtures written in the classifier's vocabulary — scored 10/10 by phrase-matching | rewritten by an agent kept blind to the signal list |
| Replay could self-score off the Receipt column | withholding moved into code |
| Baseline keyed on filename; a renumber orphaned every key silently | keyed on `repo/slug`; orphans now **fail loudly** |
| Worktree directory names hijacked repo attribution | resolve a worktree to its owning repo via its `.git` file |
| `kb-note` / `kb-ingest` commands in the docs did not run | corrected to `notes-sync.sh`; `KB_NOTES_ROOT` documented |

---

## Deployed across all three programs, 2026-08-18

| repo | basis | record lint | calcguard physics |
|---|---|---|---|
| lgs-truss-designer | ✅ | ✅ 11 records | ✅ in use |
| CFS_Box | ✅ 6 standards | ✅ | ✅ **wired, and it found a defect** |
| CFS-PROFILE | ✅ | ✅ | — |

The skill is GLOBAL (symlinked), so judgment already applied everywhere; the enforcement
half is what landed. `calcguard.judgment_lint` ships **in the package** — calcguard
installs as a COPY, not editable, so a consuming repo cannot reach `skills/`.

⚠ **Pin calcguard >= `cd706ea`.** CFS_Box and CFS-PROFILE both shipped briefly with a pin
predating `judgment_lint`, green locally only because their venvs had been upgraded by
hand. The tests were green and the declaration was broken at the same time.

### What calcguard found on its first run in CFS_Box

```
sum(w*L) over member loads  =  8.5063 kip
1.5 x reported total        =  5.1432 kip     +65%
```

`self_weight_udls`' docstring says the distributed total equals box_weight; the UDLs carry
member self-weight that `total` does not. **`total` feeds the lifting case, so the reported
module weight is ~40% LOW — unconservative for crane and rigging selection.** Left
`xfail(strict=True)`: which number is right is an engineering decision, not a refactor.
The solver is NOT implicated — `sum(Rz)/sum(w*L)` measured 1.0000.

Two other long-standing CFS_Box failures were diagnosed and are NOT defects: the deck-tie
test strips ties and makes the model under-braced, so the engine's own stability guard
correctly refuses; and `test_unknown_combo_raises` is stale, since the function was
deliberately made graceful.

## Still to work

### 1. J4.3.1 branch-selection oracle gap — blocked on documents

`TE-0015` Example 8F sits at `t2/t1 = 2.52` where all three branches agree; its own test
file records *"moving the 2.5 threshold to 3.0 leaves this file green."* Nothing on file
exercises the branch boundaries.

**Acquire RP-0581 and RP-0630.** Recorded in `lgs-truss-designer/JR-0001` §7. A
verification gap — belongs to calcguard, not to judgment.

### 2. Run the replay on every signal edit

That is when the evidence goes stale. Warm the model first — 20 GB, and Ollama evicts on
`keep_alive` expiry.

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"deepseek-r1:32b","prompt":"","keep_alive":"90m"}' >/dev/null
.venv/bin/python skills/engineering-judgment/acceptance/replay.py --model deepseek-r1:32b
EJ_REGRESSION=1 .venv/bin/python -m pytest tests/test_skill_acceptance.py -k regression -q
```

**Budget properly:** ~35 min for the fixtures (10 × 5), ~45 min for the regression
(11 records × 5). A too-short `timeout` kills it mid-run and reads like a failure — that
happened once.

### 3. Watch FORK-9 → signal 6

The one genuine over-fire, **4/5 runs**. That context never mentions worked examples,
tools or closed forms, yet signal 6 fires. Harmless under "at least" scoring; it is the
leading indicator of the tax if it spreads.

### 4. Records outpace the baseline

Every new record is **skipped** until it is in `record-baseline.json`. Re-capture
deliberately with `--capture-baseline` as records are added. **Never re-capture to turn a
red test green.**

---

## Things that will bite you

- **One draw is a sample, not a measurement.** Ollama is not bitwise deterministic on GPU
  even at `temperature: 0` — the same fixture returned `[4]` then `[4,8]` on consecutive
  calls on an idle machine. Three agreeing draws is not proof either; that mistake
  produced four "findings" that were noise, and one wrong retraction.
- **JR numbers are not stable.** A parallel session renumbered records and every
  filename-keyed baseline entry orphaned at once. Identity is `repo/slug`. Refer to a
  record as `repo/JR-NNNN` in prose; never key machinery on the number.
- **Worktrees duplicate records.** `~/projects/lgs-*` are worktrees of
  `lgs-truss-designer` holding the same files. The replay de-duplicates by slug and
  attributes to the main checkout (`.git` as a DIRECTORY, not a file).
- **Never RAG a clause number.** Asking for J4.3.1 returned NFPA 13 sprinkler standards
  plus "the provided context does not contain any reference to section J4.3.1" — while
  the clause sat in `CS-0125`. Use `vault-sections`, then read the PDF.
- **After `git checkout -- <file>`, re-run the tests.** It restores to HEAD, which may
  predate your own uncommitted work. It silently reverted a fix once; the orphan gate
  then passed and a "fix" commit shipped containing **zero source**.
- **A passing gate is not *the* passing gate.** Both worst bugs here were guards that
  stopped guarding without saying so. Make the miss loud.
- **Do not write the contiguous bigram `no`+`rule` in any skill file.** The
  prompt-injection defender matches it as a DAN pattern and fires HIGH severity on every
  read.
- **`lgs-truss-designer` is worked in parallel.** `git fetch` and `git worktree list`
  before branching; use a worktree, never the main checkout.
- **This repo is public.** Skill files name AISI clauses and repo names, consistent with
  what the README already discloses. No client data.

---

## Where things are

| | |
|---|---|
| Skill source | `skills/engineering-judgment/` |
| Usage guide | `skills/engineering-judgment/README.md` — read this first |
| Spec / plan | `docs/superpowers/specs/`, `docs/superpowers/plans/` |
| Parked material | `docs/parked-sealed-project-review.md` — sealed-project review, deliberately outside the skill |
| Records | `<repo>/docs/judgments/JR-NNNN-*.md`, plus a copy in the `notes` RAG workspace |
| Find every record | `find ~/projects -path '*/docs/judgments/JR-*'` |
