# calcguard

**Executable physics assertions for engineering calculation programs.**

You are replacing paid engineering software with your own code. The thing paid
software gives you that your own code does not is a *documented basis for
trusting it*. calcguard is that basis, made executable.

---

## Why this exists

Six defects in a cold-formed-steel truss engine passed a **1277-test suite**.
Two were unconservative and in the shipped design path — the headline strength
number moved 98.10 % → 85.38 % once fixed.

| defect | what actually caught it |
|---|---|
| a parameter sweep never built a truss with an overhang | reading *why* tests skipped |
| a truss type advertised a knob it always refused | fixing the one above |
| axial force reported at the wrong member end | an independent tool |
| fixed-end forces subtracted where they must be added | an independent tool |
| a stale member length in a new code path | an independent tool |
| the design check sized members on the end moment, 56 % low | an independent tool |

**Not one was caught by the tests.** The suite was thorough about *behaviour* and
blind to *physics*. A behavioural test asks "does this return what it returned
last week"; it never asks "does this structure balance".

A `karpathy-guidelines` skill was loaded throughout and caught none of them,
because prose guidance depends on being applied by a tired human or a hurried
model. **An assertion that runs in CI does not depend on anyone remembering it.**

That is the whole thesis.

---

## What it stands for

Four ideas, in priority order.

### 1. Physics is checkable; behaviour is not enough

Every calculation obeys laws that hold regardless of what the code does. A
structure balances. A free end carries nothing. Doubling the load doubles the
force. A symmetric structure gives symmetric answers. These are *assertions*,
not opinions, and they fail loudly on a wrong implementation.

### 2. An assertion that cannot fail is worse than no assertion

It reads as safety and provides none. So **every guard here is tested in both
directions** — it must fire on broken input and stay silent on correct input.
Two things in the session that produced this package were exactly this failure:
a CI check that reported green having reviewed nothing, and a test suite whose
moment assertions all used `abs()`, hiding a sign error for months.

### 3. Rank your evidence, and record which kind you have

Not all verification is equal, and two kinds are routinely confused:

- **Physics** (forces, deflections) can be checked against an independent
  computation — another solver, a closed form, a conservation law.
- **Code compliance** (capacity per AISI/ACI/AISC) *cannot*. There is nothing to
  cross-check against but the standard's own text and its published examples.

Saying "verified" without saying which kind you have is how a program ends up
with verified demand and unverified capacity — exactly where the truss engine
sat after its first validation pass.

### 4. Verification accumulates

A verification done once and lost is one you will pay for again. Records are
written down, committed, and **consulted before redoing the work**.

---

## The oracle ladder

Ranked by independence from the thing being checked.

| tier | source | independence | cost |
|---|---|---|---|
| **0** | closed-form and limiting cases | total, and free | low — **mandatory** |
| 1 | published worked examples (AISI/AISC/ACI manuals) | high, citable in a sealed package | medium |
| 2 | independent software | high, broadest coverage | high, needs a licence |
| 3 | your own hand calculation | low — your reasoning checking your program | medium |

**Every program must clear tier 0.** It is free and catches whole classes of
error. Anything a PE seals needs at least one of tiers 1–3. Tier 3 alone is
never sufficient.

---

## Install

```bash
git clone git@github.com:CarlosAtomic/calcguard.git ~/projects/calcguard
```

Into whichever project needs it, using **that project's** interpreter:

```bash
/path/to/project/.venv/bin/pip install -e ~/projects/calcguard
```

Editable (`-e`) on purpose: one source of truth shared by every calculation
program, so a guard improved for one is improved for all.

Verify:

```bash
/path/to/project/.venv/bin/python -c "import calcguard; print(calcguard.__version__)"
```

Requires Python ≥ 3.12 and numpy. Nothing else.

---

## Use

### Tier 1 — needs nothing but numbers

```python
from calcguard import (assert_signed, assert_matches_closed_form,
                       assert_bounded_both_sides, assert_scales,
                       assert_monotonic, assert_coverage,
                       assert_schema_matches_capability)

# Signs matter. abs() would call these equal, and that is how a sign error
# survived months of green tests.
assert_signed(moment_at_pin, 0.0, abs_tol=1e-9, what="end moment")

# Check against something hand-derivable, and NAME the formula.
assert_matches_closed_form(mid_moment, w * L**2 / 8, cite="wL^2/8")

# Both sides. `error <= budget` is passed for free by any bug that ZEROES
# the error -- for instance by reporting no force at all.
assert_bounded_both_sides(residual, lo=0.5, hi=1.5, what="residual")

# Doubling the span must quadruple the moment. A result that does not move
# with its input usually means the input is not being read.
assert_scales(moment_for_span, x=60.0, factor=2.0, power=2)

assert_monotonic(capacity_for, xs=[0.033, 0.045, 0.057], direction="increasing")

# A skipped case is not a passing case, and the two look identical in CI.
assert_coverage(built=len(built_cases), total=len(all_cases), floor=0.9)

# A knob offering a value that is always refused is a defect the user meets
# and the tests never do.
assert_schema_matches_capability(declared=ui_params, supported=engine_params,
                                 what="overhang")
```

### Tier 2 — needs a ~20-line adapter

```python
from calcguard import assert_equilibrium, assert_free_boundary_carries_nothing
from calcguard.protocols import EndForces, Geometry, PointLoad, Reaction

class MyAdapter:
    def __init__(self, model, result): self.m, self.r = model, result
    def members(self): return [m.id for m in self.m.members]
    def member_end_forces(self, mid):
        Ni, Nj = self.r.member_axial[mid]
        _, Vi, Mi, Vj, Mj = self.r.member_forces[mid]
        return EndForces(Ni, Nj, Vi, Vj, Mi, Mj)
    def member_geometry(self, mid): ...      # Geometry(length, cos, sin)
    def member_transverse_load(self, mid): ...
    def applied_loads(self): ...             # [PointLoad(fx, fy), ...]
    def reactions(self): ...                 # {node: Reaction(rx, ry, mz)}

assert_equilibrium(MyAdapter(model, result))
assert_free_boundary_carries_nothing(adapter, mid=7, end="j")
```

**Start with `assert_equilibrium`.** It catches three of the six motivating
defects on its own, because neither a sign error nor a stale length nor a force
at the wrong end can satisfy it.

One caveat before writing a minimal adapter: that power sits almost entirely in
the **per-member** axial check, not the global force sum. Global reactions
balance whether or not the axial is placed at the wrong end — measured, on the
very cantilever that exposed the defect. An adapter exposing only
`applied_loads` and `reactions` gives a guard that looks the same and catches
far less. Implement `member_end_forces`, `member_geometry` and
`member_transverse_load` too.

### Tier 3 — comparison against an external reference

```python
from calcguard import compare_to_reference

table = compare_to_reference(
    ours=our_axial_by_member,
    reference=published_axial_by_member,
    reference_sign="compression-positive",   # Calcs.com; ours is tension-positive
    unit_factor=1.0,
    tol_pct=1.0)

table.assert_within()          # fails the build
print(table.to_markdown())     # feeds the verification record
```

Two traps it handles so you need not remember them:

- **Sign convention.** Calcs.com reports compression-positive. Comparing without
  flipping makes a *correct* engine look catastrophically wrong.
- **What "1 %" means.** Agreement is measured against the **peak** quantity in
  the model, not per item. A 53 % error on a member carrying 10 lb is noise; the
  same percentage on a governing member is not.

---

## The verification record

*(Designed, not yet implemented — see Roadmap items 1 and 2.)*

A comparison that passes and is then forgotten has to be redone. Records are
meant to be **durable, committed, and consulted first**:

- **`VERIFICATION.md` per program**, generated from the harness and committed
  with the code: what was compared, against which oracle tier, the per-item
  table, the agreement achieved, and — mandatory — a **"Not covered"** section.
  That section is what keeps a record honest; it is easy to write "verified"
  and stop when capacity has no reference at all.
- **Assumptions travel with the numbers.** Sign convention, units, boundary
  conditions, which edition of which standard, and any modelling difference that
  had to be replicated before comparing. Without these a record cannot be
  reproduced or trusted a year later.
- **Consult before recomputing.** Before verifying a clause or a quantity, check
  whether a prior record already covers it, at what tier, and under what
  assumptions. A verified clause becomes a **source of truth for other
  programs** — the same AISI equation checked once should not be re-derived in
  the next project.

---

## What it deliberately is not

- Not a solver, a units library (`pint` exists), a plotting tool, or a report
  formatter.
- Not domain-aware. calcguard does not know what a truss is; the adapter does.
- Not an auto-fixer. It reports and fails; a human decides.
- Not a CI configuration. It is a pytest-compatible library; the repo wires it up.

Kept small so it actually gets used.

---

## Roadmap

Named so they are not forgotten:

1. **Verification record generator** — `VERIFICATION.md` from a
   `ComparisonTable`, with the mandatory "Not covered" section and an
   assumptions block.
2. **Verification index** — a machine-readable ledger of what has been verified,
   at which oracle tier, so prior work is consulted before being repeated.
3. **`assert_symmetric`** and `assert_reactions_balance_applied_load`.
4. **The `engineering-calc-verification` skill** — three stages (write, assert,
   validate) plus `references/traps.md`, the concrete failure modes with the
   real example that produced each.

---

## Testing

`tests/test_acceptance_lgs.py` reproduces all six motivating defects as minimal
fixtures and requires calcguard to fail on every one, plus a companion test that
every assertion stays silent on correct input.

```bash
.venv/bin/python -m pytest tests/ -v
```

**A verification tool that cannot catch known bugs is decorative.** That suite is
the proof this one is not.
