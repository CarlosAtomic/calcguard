# engineering-judgment — how to use it

A Claude Code skill that resolves **forks**: the moments while implementing a code
clause when the standard does not uniquely determine the answer, and someone has to
choose.

`SKILL.md` is what Claude reads. **This file is for you.**

---

## What it is, in one paragraph

calcguard asserts physics — equilibrium, sign, scaling, closed form. It answers *does
this satisfy the equation it was pointed at?* This skill answers what comes earlier:
**which clause, which edition, which reading?** Where the standard settles it, it cites
and moves on. Where it does not, it produces a researched, cited record and hands the
decision to you. **The two tools never exchange data.** calcguard is untouched.

## What it is not

- Not a review gate. It has no schedule and nothing to block.
- Not a sealed-project reviewer. Permit dates, IEBC triggers, load path and
  constructability are **parked** in `references/parked-project-mode.md` and wired into
  nothing. A calc engine has no permit date.
- Not a supersession engine. It never ranks editions.
- Not an editor. It issues a record; you change the code.

---

## When it fires

Only on one of nine enumerated signals. **No signal, no invocation, no cost** — that is
the whole design. An unambiguous clause gets implemented normally and the skill stays
silent.

| # | Signal | You'd notice it as |
|---|---|---|
| 1 | Cross-reference body | "I read the whole clause and the numbers aren't in it" |
| 2 | Undefined input | "It needs a value nothing in the model supplies" |
| 3 | Ambiguous scope | "'Adjacent' could mean two things" / "two clauses both seem to apply" |
| 4 | Referenced artifact unread | "It leans on a figure I haven't opened" |
| 5 | Determination handed to you | "It says engineering judgment is required" |
| 6 | No oracle | "Nothing on file checks this branch" |
| 7 | Cross-table pairing | "Both values are right — is combining them legal?" |
| 8 | Edition delta on the path | "I'm reaching for a worked example from another edition" |
| 9 | Outside tested range | "This method was validated on something else" |

**Signals 1, 4 and 7 are mechanical** — checkable without understanding the physics —
so they survive an implementer who is confidently wrong. Trust them most. Signal 7 is
the one that caught a 1.43× unconservative pairing where both inputs were individually
correct.

---

## Three ways to use it

### 1. Let it fire on its own (the main path)

Just work. When Claude is implementing a clause and hits a signal, it stops, states the
fork in one line, researches, and brings you candidate readings instead of silently
picking one. **You don't invoke anything.**

### 2. Ask for it

```
/engineering-judgment
"which reading governs here?"
"the older edition said this — what changed?"
"is this pairing legal?"
"what's our basis for this?"
```

### 3. Point it at a clause

> "Run engineering-judgment on AISI S100-16 §J4.3.1 as implemented in lgs."

---

## What it does, step by step

| # | Step | Why it is in that order |
|---|---|---|
| 0 | Read `code-basis.toml` | The basis is a project decision, never inferred from publication dates. It **reads**, it does not interrogate you. |
| 1 | Scan the nine signals | No hit → stop, implement normally, say nothing |
| 2 | State the fork in one line | **Before** research — research done after a reading is chosen will find support for that reading |
| 3 | Write the expectation | **Before** reading sources — a number read first moves the target instead of failing |
| 4 | Research | Catalog and clause PDF, declared edition first |
| 5 | Resolve | Precedence ladder, then the conservatism rule |
| 6 | Emit | Record + vault copy + a pinning test |

Steps 2 and 3 coming before step 4 is not ceremony. It is the only defence against
reading the answer and then reasoning backwards to why it is plausible.

---

## The four verdicts

| Verdict | Means | Must state |
|---|---|---|
| **Determined** | the standard resolves it | edition + section |
| **Judged** | it does not; a reading was chosen | candidate readings, which is conservative, **what would change the choice**, who decides |
| **Insufficient basis** | the library lacks what this fork needs | the specific document to acquire |
| **Alternative means** | less conservative than the declared basis permits | named as IBC §104.11, **not applied** |

*Alternative means* is top-level so it cannot hide inside a *Judged*.

**"Insufficient basis" is a normal, valuable answer.** A resolver that always reaches a
verdict is a rubber stamp. Those gaps accumulate into your acquisition list — they tell
you exactly which documents the work actually needs.

### The conservatism rule

> A non-adopted source that makes the design **more conservative** than the declared
> basis may be applied freely, cited as judgment.
>
> A non-adopted source that makes the design **less conservative** may not be applied on
> its own authority. That is an IBC §104.11 alternative means.

You are always free to be stricter. You are never free to be more permissive without
the door the code provides. Edition deltas produce a **diff as evidence**, never a
verdict that one edition supersedes another.

---

## What comes out

A record at `docs/judgments/JR-NNNN-<slug>.md` **in the repo whose code it governs** —
so it shows in the diff and travels with the code:

```yaml
---
id: JR-0001
clause: AISI S240-20 §E4.5.1
basis: AISI S100-16 (2020) w/S2-20    # full designation, supplement included
repo: lgs-truss-designer
commit: <sha>
signals: [2, 3]
verdict: judged
decided_by: Carlos                     # never the skill
pin: tests/test_gusset_layout.py::test_wrap_around_pair_is_adjacent
---
```

Seven body sections: the fork · the expectation (written before research) · candidate
readings · research with citations · resolution + ladder rung · **what would change
this** · **Not covered** (mandatory — it is what keeps the record honest).

### The pin

Every `judged` record names a test asserting the chosen reading, whose docstring cites
the record id. Reverse the reading and the build fails, pointing at the record. **Prose
explains; the assertion enforces.** A `determined` record needs no pin.

### The vault copy

```bash
~/projects/spark-powerhouse/ingest/.venv/bin/kb-note decision \
  "JR-0001 <title>" --project lgs-truss-designer --source JR-0001 \
  --tags "judgment,AISI" --body "<resolution>"
```

→ `Inbox/` → 03:15 `notes-sync.sh` → `Decisions/` → `notes` workspace.

Three things to know:
- `decision` is the right type — an unrecognised type falls back to `Findings`.
- Find prior judgments with **`llocal rag notes`**, *not* `vault-search`. The catalog
  indexes PDFs; `JR-` records live in `notes`.
- Repo-visible immediately, vault-discoverable after 03:15. For same-day lookup run
  `kb-ingest --source notes` manually.

---

## Research: the part that bites

**Never grep or RAG the vault for a clause number.**

Measured 2026-08-15 — asking the RAG *"What does J4.3.1 say about linear
interpolation?"* returned **"the provided context does not contain any reference to
section J4.3.1"** and cited **NFPA 13, sprinkler systems**. The clause was in CS-0125
the entire time. Section identifiers do not embed; vectors match concepts, not numbers.
That answer reads like a fact about your corpus and is a fact about the instrument.

**Correct order:**

```bash
~/bin/vault-sections "gusset plate" --topic CS --json      # 0.3 s — names the document
~/bin/vault-search "distortional buckling" --json          # 0.3 s — basis gate
pdftotext -layout "<the PDF>" - | grep -n -A15 "J4.3.1"    # the authority itself
llocal rag notes "gusset Leff adjacency"                   # prior judgments
codes-table                                                # every edition, ranked never
```

**`llocal research` is for concept questions and takes minutes.** ~17 s per workspace,
16 workspaces, 4 at a time ≈ 70 s of retrieval plus a merge synthesis. A 120 s timeout
kills it; so does 300 s. It is not broken.

**Warm the model first** — `qwen3.6` is 23 GB and Ollama evicts it:

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"qwen3.6","prompt":"","keep_alive":"30m"}' >/dev/null
curl -s http://localhost:11434/api/ps        # confirm resident, then launch
```

**A killed run is not an empty result.** If it times out, the research leg did not
execute — that is different from "searched, found nothing."

---

## Worked example — §J4.3.1 in lgs, steps 0–5

A real run, 2026-08-15.

**Basis:** `AISI S100-16 (2020) w/S2-20`, read from `code-basis.toml`.

**Signals fired:** 6 (no oracle), 2 (`Pnvs` undefined), 5 (J4.3.2 defers to the maker),
9 (one manufacturer's ESR applied generically), 8 (S3-22 logic in play).

**Expectation, written before researching** — and all three held:

1. the clause text will support the engine's interpolation reading ✅
2. `pns_thin ≤ pns_thick` always, so interpolation is monotonic ✅
3. no worked example on file in `1.0 < t2/t1 < 2.5` ✅

**Findings:**

| | Verdict |
|---|---|
| Interpolation reading (`connections.py:170-172`) | **Determined** — clause text is explicit, cite CS-0125 §J4.3.1 p. 113 |
| φ for the screw-shaft limit state | **live fork** — J4.3.2 permits a K2.1 test-based φ the engine never engages, and its sentence admits two readings. Flat 0.50 is the conservative floor, so no sealed number moves; the *provenance* is wrong |
| Where `Pnvs` comes from | **live fork** — one maker's table (Hilti ESR-2196/3891) served for any matching designation. Ladder rung 3: configuration match is a gate, not a preference |
| Branch selection | **Insufficient basis** — the oracle says so itself: *"Moving the 2.5 threshold to 3.0 leaves this file green."* Acquire RP-0581, RP-0630 |

Note what the skill did **not** do: it declined to manufacture a fork where the clause
text was clear, and it stopped before deciding the two live ones.

---

## Verification status — read this before trusting it

`tests/test_skill_acceptance.py` (in the calcguard suite) guards the fixtures and the
signal list against drift. It **cannot** check semantics — that is the replay logged at
the bottom of `acceptance/forks.md`.

Replay, 2026-08-15, under blind conditions (fresh agent per case, shuffled, Receipt
column withheld, case identity and the existence of a control withheld):

- **6 of 9 scored FORK cases passed**
- **the negative control returned `[]`** — the result that makes the rest mean anything
- ⛔ **FORK-2, FORK-4 and FORK-8 are UNSCORED, not passed.** Five dispatches returned no
  answer. **So signals 2, 4, 8 and 9 have no replay evidence.** Signal 8 is the notable
  gap — it was narrowed the same day and FORK-4 is its only fixture.
- Two defensible over-fires logged. FORK-3 also returning signal 4 exposes a real seam:
  **signals 1 and 4 overlap whenever the cross-referenced target is still unread.**

The fixtures were rewritten before that run because an earlier pass scored 10/10 by
phrase-matching the signal table's own wording. A replay that scores on shared
vocabulary proves nothing.

---

## Install and maintenance

```bash
ln -s /home/atomicjr/projects/calcguard/skills/engineering-judgment \
      /home/atomicjr/.claude/skills/engineering-judgment
```

**A symlink, never a copy** — `reference-library` was installed as a copy and silently
diverged from its repo. Global, so there is nothing to install per project.

`calcguard`'s Python package is **byte-identical**; `lgs-truss-designer`, `CFS_Box` and
`CFS-PROFILE` are unaffected and need no reinstall.

### Gotcha

Do not write the contiguous bigram `no`+`rule` in any skill file. The local
prompt-injection defender matches it as a DAN "No-rules mode request" and fires HIGH
severity on **every read**. Signal 5 was reworded for exactly this. A security hook that
cries wolf on a core file teaches you to ignore it.
