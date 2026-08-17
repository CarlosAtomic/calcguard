# Acceptance fixtures — forks that actually happened

Each case states the situation with the **resolution withheld**. The skill passes a
case when scanning it trips at least the expected signals.

`tests/test_skill_acceptance.py` checks the structure of this file. It cannot check
the semantics — that is the replay in Task 10.

Format is load-bearing: `**Expected signals:**` takes comma-separated integers, or
`none`.

---

## FORK-1 — gusset joint adjacency

**Repo:** lgs-gusset
**Clause:** AISI S240-20 §E4.5.1
**Expected signals:** 3

**Context:** I'm working through E4.5.1 for a gusset where several members meet at a
panel point. The clause sizes the gusset off the effective length across members it
calls "adjacent." Listed in order around the joint, the first and last members sit right
next to each other if you wrap around the node — but they're at opposite ends if you
just read the list top to bottom. Picking one ordering over the other changes which pair
I measure `Leff` between, and that changes the capacity I get.
---

## FORK-2 — the effective length the engine cannot compute

**Repo:** lgs-truss-designer
**Clause:** AISI S240-20 §E4.5
**Expected signals:** 2

**Context:** The E4.5 gusset provision needs `Leff` as an input. I traced where that
number is supposed to come from, and it's set by the plate shape and the fastener
pattern the fabricator draws up — that only exists on the shop drawing. I went through
every field the analysis model currently populates and there's nothing in there that
gives me that dimension, and I can't back it out of anything else the model already has.
---

## FORK-3 — the bolt clause with no numbers in it

**Repo:** lgs-bolts
**Clause:** AISI S100-16 §J3.4
**Expected signals:** 1

**Context:** Trying to code up bolted shear per J3.4. Read the whole section top to
bottom looking for the shear stress value and the resistance factor to plug in — they're
not there. The text tells you the requirement applies and sends you somewhere else for
the numbers; nothing material-specific is actually written in J3.4 itself.
---

## FORK-4 — the clause that did not change and the figure that did

**Repo:** lgs-truss-designer
**Clause:** ASCE 7 §7.6.1
**Expected signals:** 4, 8

**Context:** Pulled both ASCE 7 editions we have on file to double-check the snow
provision in §7.6.1 before coding it. Word for word, the clause text is the same in both
copies. It leans on a figure though, and I haven't actually opened that figure in either
edition yet — just read around it. Our project's declared code basis calls out one
specific edition of the two.
---

## FORK-5 — the branch with nothing to check it against

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §J4.3.1
**Expected signals:** 6

**Context:** Finished coding the J4.3.1 screw-connection branch and it spits out a
number. Went looking for anything to check it against: the worked examples in the AISI
manual all use a different screw arrangement than what we've got, the one commercial
tool I know of that handles this case isn't something we're licensed for, and the
formula itself is a curve fit — there's no simple edge case where I can set something to
zero and know what the answer should be.
---

## FORK-6 — two elastic buckling clauses for one member

**Repo:** CFS_Box
**Clause:** AISI S100-16 §E2.2 / §E2.3
**Expected signals:** 3, 6

**Context:** Need `Fcre` for an axial capacity check, and there are two sections in S100
that both cover elastic flexural-torsional buckling — E2.2 and E2.3. Read through the
scoping text for each trying to work out which one applies to the member I've got, and
their conditions overlap for this case; I can't tell which one is supposed to win. On
top of that, I don't have a worked example on file for either branch using this section
shape.
---

## FORK-7 — two correct tables, combined

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §J3 with Appendix A
**Expected signals:** 7

**Context:** Put together a bolted-connection capacity by pulling the nominal shear
stress out of one table and a geometric limit out of a separate clause. Checked both
numbers against their own sources and they're both right. What I haven't done is confirm
the standard actually lets you combine those two specific provisions — whether they're
meant to apply to the same scope of connection or not.
---

## FORK-8 — a method borrowed from the wrong material

**Repo:** lgs-gusset
**Clause:** AISI S240-20 §E4.5.1
**Expected signals:** 9

**Context:** For the gusset compression check I pulled in the AISC Whitmore section
method — it's the one I know for this kind of check, but it was validated on hot-rolled
plate. The plate I'm actually checking is cold-formed and thinner than anything Whitmore
was tested on. Noticed afterward that AISI has its own plate-buckling provision meant
for this situation.
---

## FORK-9 — the clause that hands it back to you

**Repo:** lgs-truss-designer
**Clause:** AISI S240-20 §E4.5.2
**Expected signals:** 5

**Context:** Checking gusset-plate tension — gross yielding, net rupture, shear lag out
of Chapter D, plus tear-out at the fasteners. Went to the S240 commentary for this
clause and it says outright that figuring out how much of the plate to include in the
gross and net area checks is up to engineering judgment. I looked for something in the
standard that draws that boundary for me and there isn't anything — the commentary says
it's a judgment call and leaves it there.
---

## CONTROL-1 — negative control

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §E3.2.1
**Expected signals:** none

**Context:** Coded up E3.2.1 today — the compression check where local buckling
interacts with yielding and global buckling. Easy one. The equation is written out in
the section itself with every variable defined a paragraph later, no figures or appendix
tables to go find, and it doesn't punt anything to analysis or test. Area, yield stress,
the buckling stresses — all of it already comes off the section properties the model
computes, nothing off a shop drawing, and nothing borrowed from another clause's table.
The scope paragraph names one member condition and I couldn't read it two ways. S100 is
the only edition of it we hold. The AISI manual has a worked example for this exact
section and load case and my number matched it, with the member sitting well inside the
limits the equation is written for.

**This case must trip zero signals.** A signal list that fires here is a tax on every
clause, which is the friction this skill exists to avoid.

---

## Replay log

Run it yourself — it is scripted and repeatable:

```bash
.venv/bin/python skills/engineering-judgment/acceptance/replay.py --model deepseek-r1:32b
```

`replay.py` builds the prompt, so the withholding rule cannot be forgotten: Receipt
column stripped, case ids dropped, order shuffled.

### 2026-08-17 — deepseek-r1:32b, **5 runs per case, majority ≥3/5**

Quiet machine (no other model resident). Parenthesised = `signal:hits-out-of-5`.

| Case | Expected | Majority | Frequencies | |
|---|---|---|---|---|
| FORK-1 | 3 | `[3]` | 3:5 | pass |
| FORK-2 | 2 | `[2]` | 1:1 2:5 | pass |
| FORK-3 | 1 | `[1]` | 1:5 | pass |
| FORK-4 | 4, 8 | `[4,8]` | 4:5 **8:5** | pass |
| FORK-5 | 6 | `[6]` | 6:5 | pass |
| FORK-6 | 3, 6 | `[3,6]` | 3:5 6:5 | pass |
| FORK-7 | 7 | `[7]` | 7:5 | pass |
| FORK-8 | 9 | `[9]` | 9:5 | pass |
| FORK-9 | 5 | `[5,6]` | 3:1 5:5 **6:4** | pass, over-fires 6 |
| CONTROL-1 | none | `[]` | — | **pass, nothing fired in any run** |

**10 pass, 0 fail, 0 model errors.**

## ⛔ Retractions — the earlier single-draw results were samples, not measurements

`score()` was called **once per case** before 2026-08-17. Ollama is not bitwise
deterministic on GPU even at `temperature: 0` — non-associative float reduction flips a
borderline token, and a borderline token flips a signal. Measured on an idle machine:
the same short fixture returned `[4]` and then `[4,8]` on consecutive calls.

Three agreeing draws is not proof either. That was the basis for calling the replay
"deterministic", and it was wrong.

**What the 5-run frequencies overturned:**

| Earlier claim | 5-run reality |
|---|---|
| "Signal 8 does not reliably fire" | **8:5** on FORK-4 — fires every run. The rewording works; the lone `[4]` was the outlier |
| "Signals 1 and 4 overlap whenever the cross-referenced target is unread" — logged as a structural seam | FORK-3 is **1:5** and signal 4 never appeared. **Not a thing.** |
| "FORK-7 over-fires 3" | 7:5, signal 3 never appeared |
| "FORK-2 over-fires 1" | 1:**1** of 5 — noise |
| "10 pass, deterministic" (2026-08-16) | one draw per case; the number happened to hold, the method did not |

The one **real** over-fire is FORK-9 → signal 6 at **4/5**. Worth watching; the context
never mentions worked examples, tools or closed forms.

**With a stochastic scorer, an n=1 finding and an n=1 retraction are equally worthless.
Both were made here.**

### Why the control result is the load-bearing one

CONTROL-1 fired **nothing across five runs**. A scorer that pattern-matches would light
the control first, and two FORK cases do carry minority noise (1:1, 3:1) — so the
instrument is not simply returning the expected set. The negative held while the
positives wobbled, which is the shape that makes the positives worth something.

### Evidence quality per signal

Signals **3, 4, 5, 6** carry REAL evidence — they fired on records that actually
happened. **1, 2, 7, 8, 9** are synthetic-only: scored and passing, never yet triggered
by real work. `tests/test_skill_acceptance.py` prints the label per signal; it does not
fail on the gap.

The fixtures were rewritten blind (`49048d8`) before any of this, because an earlier
pass reached 10/10 by phrase-matching the signal table's own wording.

