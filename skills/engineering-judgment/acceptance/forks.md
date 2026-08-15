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

**Context:** E4.5.1 sizes a gusset from the effective length across members meeting
at a panel point. The clause governs members that are "adjacent." At a joint where
members are ordered around the node, it is not stated whether the first and last
members — adjacent by wrapping the circle, separated by every other member if read
as a flat list — form an adjacent pair. The two readings give different `Leff` and
therefore a different capacity.

---

## FORK-2 — the effective length the engine cannot compute

**Repo:** lgs-truss-designer
**Clause:** AISI S240-20 §E4.5
**Expected signals:** 2

**Context:** The gusset provision requires `Leff`. Tracing its definition, the value
is set by the fabricated plate and fastener layout — information that lives on the
shop drawing. No input to the analysis engine supplies it, and no combination of the
engine's inputs derives it.

---

## FORK-3 — the bolt clause with no numbers in it

**Repo:** lgs-bolts
**Clause:** AISI S100-16 §J3.4
**Expected signals:** 1

**Context:** Implementing bolted connection shear. J3.4 is read in full. Its body
states the applicable requirement by pointing elsewhere; no nominal shear stress,
no resistance factor, and no material-specific value appears in the section text.

---

## FORK-4 — the clause that did not change and the figure that did

**Repo:** lgs-truss-designer
**Clause:** ASCE 7 §7.6.1
**Expected signals:** 4, 8

**Context:** Comparing two editions of ASCE 7 on file for the snow provision. The
prose of §7.6.1 reads identically between them. The section operates through a
referenced figure, which has not been opened in either edition. The declared basis
names one of the two editions.

---

## FORK-5 — the branch with nothing to check it against

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §J4.3.1
**Expected signals:** 6

**Context:** A screw-connection branch is implemented and returns a number. A search for
anything to check it against comes up empty: the AISI design manual's worked examples
all use a different fastener configuration, the one commercial tool that covers this
case is not licensed here, and the expression is a fitted empirical form with no
limiting case that pins the result.

---

## FORK-6 — two elastic buckling clauses for one member

**Repo:** CFS_Box
**Clause:** AISI S100-16 §E2.2 / §E2.3
**Expected signals:** 3, 6

**Context:** Axial capacity needs elastic flexural-torsional buckling stress `Fcre`.
Two sections address it under conditions that overlap for the member in hand, and
the standard's scoping language does not clearly assign this member to one of them.
Neither branch has a worked example on file for this section shape.

---

## FORK-7 — two correct tables, combined

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §J3 with Appendix A
**Expected signals:** 7

**Context:** A bolted-connection capacity is assembled by taking a nominal shear
stress from one table and a geometric limit from another clause. Each value is read
correctly from its own source. Whether the standard permits that specific pairing —
whether the two tables share a scope — was not checked.

---

## FORK-8 — a method borrowed from the wrong material

**Repo:** lgs-gusset
**Clause:** AISI S240-20 §E4.5.1
**Expected signals:** 9

**Context:** A gusset compression check is available as the AISC Whitmore section
method, validated on hot-rolled plate. The plate here is cold-formed steel at a
thickness well below the range in which Whitmore was tested, and AISI supplies its
own plate-buckling provision for this case.

---

## FORK-9 — the clause that hands it back to you

**Repo:** lgs-truss-designer
**Clause:** AISI S240-20 §E4.5.2
**Expected signals:** 5

**Context:** Gusset-plate tension is checked per Chapter D of S100 — gross yielding,
net rupture, shear lag — plus fastener tear-out. The S240 commentary to this clause
states plainly that "engineering judgment is required to determine the portion of the
gusset plate to be included in the gross and net area checks." No rule in the
standard fixes which portion of the plate belongs in that check; the clause hands the
determination to the implementer instead of supplying one.

---

## CONTROL-1 — negative control

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §E3.2.1
**Expected signals:** none

**Context:** A compression strength expression — local buckling interacting with
yielding and global buckling. The clause supplies the equation directly in the section
text, with every variable defined in the same section, and it does not point elsewhere
or defer to analysis, test, or judgment. Every quantity the equation needs is already
produced by the engine's existing inputs; nothing comes from a shop drawing or
fabrication detail. Its scope statement names one member condition explicitly, with no
qualifying term open to a second reading. No figure, table, or appendix is referenced.
Only one edition of this standard is on file, and this clause is unchanged within it.
A published worked example covers this exact case, and the member sits well inside the
validated range of the expression. No value from another clause or table enters the
calculation.

**This case must trip zero signals.** A signal list that fires here is a tax on every
clause, which is the friction this skill exists to avoid.
