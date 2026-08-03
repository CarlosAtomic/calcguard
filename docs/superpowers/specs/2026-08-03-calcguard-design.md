# calcguard — design

**Date:** 2026-08-03
**Status:** design, awaiting review

## 1. Why

Six defects were found in `lgs-truss-designer` on 2026-08-02/03. **Not one was
caught by its 1277-test suite.** Every one was caught either by comparing against
an independent tool or by a violated physical invariant.

| defect | what actually caught it |
|---|---|
| planarity gate never built a truss with an overhang | reading *why* tests skipped |
| a truss type advertised a parameter it always refused | fixing the one above |
| axial force placed at the wrong member end | Calcs.com |
| fixed-end forces subtracted where they must be added | Calcs.com |
| stale member length in a new code path | Calcs.com |
| design check sized members on the end moment, 56 % low | Calcs.com |

Two of these were **unconservative and in the shipped design path**. The engine's
headline strength number moved 98.10 → 85.38 % once fixed.

The suite was thorough about *behaviour* and blind to *physics*. The
`karpathy-guidelines` skill was loaded throughout and caught none of them,
because prose guidance depends on being applied. An assertion that runs in CI
does not.

That is the thesis: **encode the physics as executable assertions, and rank the
evidence that a calculation is right.**

## 2. What it is

A small Python package, `calcguard`, installed once and shared by every
engineering calculation program (`lgs-truss-designer`, `CFS_Box`, and whatever
follows), plus a skill that decides which of its assertions apply and produces
the verification record.

The package is the product. The skill is the guide to it.

## 3. Success criteria

**calcguard is done when, applied to `lgs-truss-designer` at the commit before
each fix, it fails on all six defects above.** That is the acceptance test: a
verification tool that cannot catch known bugs is decorative.

Concretely, each defect maps to an assertion:

| defect | assertion that catches it |
|---|---|
| axial at the wrong end | `assert_equilibrium` (member end forces vs applied load) |
| fef sign inverted | `assert_equilibrium`, and `assert_signed` against a closed form |
| stale member length | `assert_scales` (two members, different lengths) |
| end-moment sizing | `assert_matches_closed_form` (simply supported, `wL²/8`) |
| refusal read as a pass | `assert_coverage` (a skipped case is not a passing case) |
| parameter advertised but unusable | `assert_schema_matches_capability` |

## 4. Architecture

### 4.1 Tier 1 — domain-agnostic

No adapter. Works for any calculation, structural or not.

```python
assert_signed(actual, expected, rel=1e-9)   # refuses an abs() comparison
assert_bounded_both_sides(value, lo, hi)    # a bug that ZEROES the error passes a one-sided check
assert_scales(fn, factor=2.0)               # double the input, double the output
assert_monotonic(fn, param, direction="increasing")
assert_matches_closed_form(actual, expected, cite="wL^2/8")
assert_coverage(cases_built, cases_total, floor=0.9)
assert_schema_matches_capability(declared, supported)
```

`assert_signed` compares signed values and fails when the signs differ, even if
the magnitudes agree. It cannot detect that a caller passed `abs(x)` — nothing
can, at runtime — so it does the one thing that is possible: it makes the signed
comparison the easy path, and its failure message names the sign as the
difference. **Every moment assertion in `lgs-truss-designer` used `abs()`, which
is precisely why a sign error survived for months**: a clamped-clamped beam is
symmetric, so the error is invisible under `abs()` and the magnitude is right
either way. Catching the remaining `abs()` habit is the WRITE stage's job, not
the library's.

`assert_schema_matches_capability` compares what a program *advertises* (its
parameter schema, its UI controls) against what it can actually honour. A knob
that always refuses is a defect the user meets and the tests never do.

### 4.2 Tier 2 — conservation

Requires a small adapter (§4.4).

```python
assert_equilibrium(adapter, tol=1e-9)                # per member AND globally
assert_reactions_balance_applied_load(adapter)
assert_free_boundary_carries_nothing(adapter, node)
assert_symmetric(adapter, mirror_map, quantities=("axial", "moment"))
```

`assert_equilibrium` is the highest-value item in the package: **it catches three
of the six defects on its own.** A member's end forces must balance the load
applied to it, and the sum of reactions must equal the sum of applied loads.
Neither can be satisfied by a sign error or a stale length.

### 4.3 Tier 3 — reference comparison

```python
table = compare_to_reference(ours, reference, tol_pct=1.0,
                             sign_convention="tension-positive",
                             reference_sign="compression-positive",
                             units="lb")
table.assert_within()          # fails the build
table.to_markdown()            # feeds the verification record
```

It handles **sign convention and unit conversion explicitly**, because that is
where the traps are: Calcs.com reports compression-positive, and comparing
without flipping makes a correct engine look catastrophically wrong.

The table reports agreement **as a fraction of the peak quantity in the model**,
not per item. A 53 % error on a member carrying 10 lb is noise; the same
percentage on a governing member is not. Both are reported; only the second
fails the build.

### 4.4 The adapter

The entire coupling surface. Roughly twenty lines per program.

```python
class StructuralAdapter(Protocol):
    def members(self) -> Iterable[MemberId]: ...
    def member_end_forces(self, mid) -> EndForces:   # Ni, Nj, Vi, Vj, Mi, Mj
    def member_geometry(self, mid) -> Geometry:      # length, direction cosines
    def applied_loads(self) -> Loads: ...
    def reactions(self) -> Mapping[NodeId, Reaction]: ...
```

Tier 1 needs no adapter. Tier 3 needs no adapter. Only Tier 2 does.

### 4.5 The oracle ladder

Ranked by independence from the thing being checked. Every program must clear
tier 0. Anything a PE seals needs at least one of 1–3.

| tier | source | independence | cost |
|---|---|---|---|
| **0** | closed-form and limiting cases | total, and free | low — **mandatory** |
| 1 | published worked examples (AISI/AISC/ACI manuals) | high, and citable in a sealed package | medium |
| 2 | independent software | high, broadest coverage | high, needs a licence |
| 3 | your own hand calculation | low — your reasoning checking your program | medium |

Tier 0 is mandatory because it is free and catches whole classes of error.
Tier 3 alone is never sufficient.

**A distinction the ladder must record:** *physics* (forces, deflections) can be
verified against an independent computation. *Code compliance* (capacity per
AISI/ACI) cannot — there is nothing to cross-check against but the standard's own
text and its published examples. The record states which kind each entry is.

### 4.6 The verification record

`VERIFICATION.md`, generated from the harness and committed with the code.
The template **mandates a "Not covered" section.** That is what kept the
`lgs-truss-designer` report honest: it would have been easy to write "verified"
and stop, when capacity had no reference at all.

## 5. The skill

`engineering-calc-verification`, three stages, each invocable alone.

1. **WRITE** — the short discipline rules, consulted while writing calc code.
2. **ASSERT** — choose the invariants for this domain, generate the test module.
   Default entry point.
3. **VALIDATE** — walk the oracle ladder, run the comparison, emit the record.

`references/traps.md` carries the concrete failure modes, each with the real
example that produced it.

## 6. Out of scope

Deliberately excluded, to keep this small enough to finish and to invoke:

- No solver, no units library (`pint` exists), no plotting, no report styling.
- No domain knowledge. calcguard does not know what a truss is; the adapter does.
- No auto-fixing. It reports and fails; a human decides.
- No CI configuration. It is a pytest-compatible library; the repo wires it up.

## 7. Testing

calcguard's own tests are the six defects, reproduced as minimal fixtures:
a vertical cantilever whose free end must carry nothing, a two-span beam whose
simply supported end must carry no moment, two members of unequal length, a
sweep where a refusal must not read as a pass.

Every assertion is tested in both directions — it must fire on the broken case
and stay silent on the correct one. An assertion that cannot fail is exactly the
problem this package exists to solve.
