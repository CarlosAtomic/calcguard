# Parked: sealed-project review

**Not part of this skill's sequence. Do not run any of it during clause
implementation.**

This is review material for *sealed project work* — judging whether a specific
building's calculation is correct and sealable. That is a different job from
resolving a fork in a calc engine, and mixing them produced a skill that halted on
jurisdiction and permit date while implementing a Python function.

Kept because the material is correct for its own job and worth not rewriting. It
becomes a separate skill if and when that work needs one.

**What is parked here:** permit-date governance and the concurrency question; state
and local amendments; the Chapter 35 adoption chain; IEBC triggers and existing
structures; load path continuity to the foundation; serviceability against the actual
finish rather than a default L/240; order-of-magnitude and precedent checks;
constructability, erection stability, and shipping and lifting cases for panelized
work; and the material-specific trap lists for CFS, concrete, wood, and hot-rolled
steel.

**Why none of it belongs in the fork resolver:** a calc engine has no permit date, no
jurisdiction, no drawings to check an unbraced length against, and no site. Demanding
them blocks every invocation.

---

## Salvaged: design basis

## 2. Why "current code" is not the truth of design

Four independent reasons, each of which alone breaks the assumption:

**Permit vintage.** The governing code is the one in effect when the permit application was filed, subject to the jurisdiction's concurrency period. A building permitted under the prior edition is reviewed under the prior edition. Applying the newer edition is not "conservative" — it is a different set of provisions that may be more permissive in some places and more restrictive in others, and it will not match what was approved.

**Adoption lag.** States adopt model codes on their own schedule and with their own amendments. The published edition of a model code is not the law anywhere until a jurisdiction adopts it, and the amendments frequently change the very provision at issue.

**Reference standard freezing.** A code edition adopts specific editions of the reference standards. Those adopted editions do not update when the standards organizations publish new ones. Using the current standard under an older code is one of the most common and least visible errors in practice.

**Existing construction.** An existing structure was designed to the code of its own era and remains legally conforming under that basis unless a trigger applies. Its adequacy is judged against the original basis plus whatever the alteration triggers, not against today's provisions.

The consequence for this skill: **the vault's older documents are not obsolete clutter — they are frequently the governing authority.** Treat a superseded edition in VAUL as first-class evidence, not as history.

## 3. The adoption chain and where it breaks

Trace it explicitly, one link at a time, every time:

```
Jurisdiction  →  state code + edition  →  local amendments
      →  Chapter 35 adopted reference standards (by edition)
      →  the specific provision applied in the calc
```

The chain breaks most often at the third link. A calc will correctly identify the building code edition and then reach for whichever edition of the material standard is on the engineer's desk.

**Verify the third link in VAUL, in Chapter 35 of the actual adopted code, every time.** Do not reconstruct the mapping from memory, including the mapping you believe you know well. Standards get referenced with supplements, with partial adoptions, and with amendment-level substitutions that no one remembers correctly.

## 4. Edition traps

These are the pairs that commonly get crossed. This list is a prompt to *check*, not an answer key — confirm each against Chapter 35 of the governing edition in VAUL before relying on it.

- **ASCE 7** — a building code edition does not necessarily reference the same-vintage ASCE 7. Wind speed maps, seismic parameters, and load combinations all shift between editions, so getting this wrong changes demand, not just paperwork.
- **AISI S100 / S240 / S400** — CFS standards are adopted with supplements, and the supplement matters. S240 and S400 adoption often lags S100.
- **ACI 318** — the reorganization between editions moved provisions and renumbered chapters; a section number cited without an edition is unresolvable.
- **AISC 360 / 341 / 358** — seismic provisions and prequalified connections are adopted separately from the base specification.
- **NDS / SDPWS** — these two are adopted independently and are frequently mismatched.
- **IECC / energy provisions** — Massachusetts base, Stretch, and Specialized codes diverge, and which applies is a municipal question, not a state one.

For each trap, the check is the same: what does Chapter 35 of *the adopted edition* list, and is that what the calc used?

## 5. Existing structures

For any alteration, addition, change of occupancy, or evaluation of existing framing:

1. Identify the original design code and edition. If unknown, say so — that is *Insufficient basis* for anything that depends on original capacity, and it usually points to a need for field verification or testing rather than more analysis.
2. Identify the compliance path taken under the IEBC (prescriptive, work area, or performance) — different paths trigger different requirements and mixing them is a common defect.
3. Identify which triggers are activated: gravity demand increase thresholds, lateral demand increase thresholds, change of occupancy, substantial structural alteration, and the seismic evaluation triggers.
4. Confirm that existing capacity is being assessed against the original basis plus applicable triggers — not silently re-analyzed under current provisions and then reported as deficient.

A very common finding in this category: an existing member reported as failing, when it fails only under current provisions and is not subject to any trigger that would require it to comply with them. The reverse is also common and more dangerous — a trigger is active and nobody applied it.

## Salvaged: review checklist

## 3. Load path

Follow every load from application to the foundation and confirm each element in the chain was checked and is adequate.

The typical break: a member is designed correctly, and the element receiving its reaction was never analyzed for it. Beam is fine, the post under it is undersized. Post is fine, the footing under it is sized for a different load. Shear wall is fine, the hold-down anchorage into the foundation is not.

Also check: lateral load path continuity from diaphragm to collector to vertical element to foundation; drag/collector forces at discontinuities; and transfer conditions where vertical elements do not stack.

## 4. Governing limit state

Confirm the failure mode reported as governing is physically plausible for the configuration.

A stocky member governed by global buckling, a slender one governed by yielding, a short deep beam governed by flexure rather than shear, a connection governed by a mode inconsistent with its geometry — each indicates a modeling or input error even when the arithmetic is correct.

If the calc reports a single limit state and no others, that is a flag: either the others were checked and not reported, or they were never checked.

## 5. Serviceability

Deflection limits are not a fixed number. Check the limit against the **actual finish and function**: brittle finishes, masonry veneer, glazing, tile, movement-sensitive equipment, and cumulative deflection across stacked members.

Also: total vs. live load deflection applied to the correct case, long-term creep where applicable, floor vibration for long spans and open-plan occupancies, and differential movement between adjacent systems and between dissimilar materials.

A member that satisfies a default L/240 and cracks the tile it supports has passed the check and failed the building.

## 6. Magnitude and precedent

Two independent sanity checks:

**Order of magnitude.** Does the answer sit where experience says it should for this span, spacing, and loading? Unit weight per square foot, depth-to-span ratio, reinforcement ratio, stud gauge and spacing for the height. A result off by a factor of two or more from the expected band is an input error until proven otherwise — most commonly a unit error, a decimal, or a spacing entered as a count.

**Precedent.** Compare against past comparable projects in VAUL. Consistency with prior sealed work is a signal; inconsistency is a question, not a verdict. Precedent never overrides code (see `precedence.md`).

**Utilization pattern.** A whole schedule of members at D/C between 0.95 and 0.99 suggests optimization against a model rather than design of a structure. A whole schedule at 0.3 suggests the demand is wrong. Neither is an error by itself; both are worth a question.

## 7. Constructability

A design that cannot be built as analyzed is not correct, whatever the numbers say.

- Can the connection be physically assembled and the fasteners installed and inspected in that location?
- Is there access for the tool, the welder, the torque wrench, the inspector?
- Do erection tolerances and fit-up shift the assumed geometry enough to matter?
- Is the member stable during erection, before the bracing that the analysis assumes is in place?
- Does the sequence work — can each element be placed given what is already there?
- Does it conflict with MEP penetrations, and were the penetrations accounted for in the capacity?

For panelized and modular work specifically: shipping and lifting load cases, pick-point stresses, and in-transit support conditions frequently govern over the in-service case and are frequently not checked at all.

## 8. Material-specific traps

**Cold-formed steel** — effective width vs. gross section confusion; distortional buckling omitted; web crippling at bearing and concentrated loads; screw pattern and edge distance vs. the tested value; built-up member composite action assumed without the connection to deliver it; bridging and bracing spacing assumed rather than detailed; hold-down and chord stud capacity at shear wall ends; steel thickness specified as gauge where design thickness (mils, minus coating) governs.

**Concrete** — development length and lap splice at the actual bar location and cover; punching shear at slab-column and at openings near columns; two-way slab moment distribution; anchorage to concrete with edge distance, spacing, and cracked/uncracked assumptions; construction joint locations vs. shear transfer; shoring and reshoring loads on immature concrete, which frequently exceed service loads.

**Wood** — the stack of adjustment factors, each verified rather than assumed; notching and boring limits at the actual cut locations; connection capacity with group action and row/end/edge distance; shrinkage and differential movement at multi-story bearing; ledger connections and cross-grain tension, which is the classic collapse mechanism; fire-retardant treatment strength reductions.

**Hot-rolled steel** — lateral-torsional buckling with the correct Cb and actual brace points; local buckling and section classification; connection limit states including block shear and bolt bearing; base plate and anchor rod design including the concrete breakout modes; stability requirements and second-order effects; camber vs. deflection assumptions; slip-critical faying surface condition actually specified.
