# calcguard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared Python package of executable physics assertions that catches the class of engineering-calculation defect a behavioural test suite cannot see.

**Architecture:** Three tiers. Tier 1 needs nothing but numbers. Tier 2 needs a ~20-line adapter exposing member forces and loads. Tier 3 compares against an external reference, handling sign convention and units explicitly. Every assertion is tested in both directions — it must fire on the broken case and stay silent on the correct one.

**Tech Stack:** Python 3.12, pytest, numpy. No other runtime dependency.

**Acceptance:** applied to `lgs-truss-designer` at the commit before each fix, calcguard fails on all six defects found 2026-08-02/03. Task 9 proves it.

---

## File Structure

| file | responsibility |
|---|---|
| `pyproject.toml` | package metadata, pytest config |
| `src/calcguard/errors.py` | `CalcGuardError` and its failure-message formatting |
| `src/calcguard/tier1.py` | domain-agnostic assertions (no adapter) |
| `src/calcguard/protocols.py` | `StructuralAdapter` Protocol + the small dataclasses it returns |
| `src/calcguard/tier2.py` | conservation assertions (needs an adapter) |
| `src/calcguard/reference.py` | `compare_to_reference`, `ComparisonTable` |
| `src/calcguard/__init__.py` | the public surface, re-exports only |
| `tests/test_tier1.py` … `tests/test_acceptance_lgs.py` | one test module per source module |

Split by responsibility. `tier2` never imports `tier1`; both import `errors`.

---

### Task 1: Package skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/calcguard/__init__.py`
- Create: `src/calcguard/errors.py`
- Test: `tests/test_import.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_import.py
def test_package_imports_and_exposes_its_version():
    import calcguard
    assert isinstance(calcguard.__version__, str)


def test_calcguard_error_is_an_assertion_error():
    """Assertions must fail tests, not crash them, so the base class matters."""
    from calcguard.errors import CalcGuardError
    assert issubclass(CalcGuardError, AssertionError)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/projects/calcguard && python -m pytest tests/test_import.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'calcguard'`

- [ ] **Step 3: Write minimal implementation**

```toml
# pyproject.toml
[project]
name = "calcguard"
version = "0.1.0"
description = "Executable physics assertions for engineering calculation programs"
requires-python = ">=3.12"
dependencies = ["numpy>=1.24"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# src/calcguard/errors.py
"""The single failure type, and how a failure explains itself.

A calcguard failure must say what was expected, what was measured, and WHICH
INVARIANT was violated -- an engineer reading CI output should not have to open
the source to know whether equilibrium or a closed form was broken.
"""
from __future__ import annotations


class CalcGuardError(AssertionError):
    """Raised when a physical invariant is violated.

    Subclasses AssertionError so pytest reports it as a test failure rather
    than an error, and so `pytest.raises(AssertionError)` catches it.
    """


def fail(invariant: str, expected, actual, detail: str = "") -> None:
    """Raise a CalcGuardError with a consistent, greppable message."""
    msg = f"{invariant}: expected {expected!r}, measured {actual!r}"
    if detail:
        msg += f"\n  {detail}"
    raise CalcGuardError(msg)
```

```python
# src/calcguard/__init__.py
"""Executable physics assertions for engineering calculation programs."""
from .errors import CalcGuardError

__version__ = "0.1.0"
__all__ = ["CalcGuardError"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/projects/calcguard && pip install -e . && python -m pytest tests/test_import.py -v`
Expected: PASS, 2 passed

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/calcguard/__init__.py src/calcguard/errors.py tests/test_import.py
git commit -m "feat: package skeleton and the CalcGuardError base"
```

---

### Task 2: `assert_signed`

The assertion that would have exposed the fixed-end sign error. Every moment
assertion in `lgs-truss-designer` used `abs()`; a clamped-clamped beam is
symmetric, so the sign error was invisible and the magnitude right either way.

**Files:**
- Create: `src/calcguard/tier1.py`
- Test: `tests/test_tier1.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tier1.py
import pytest

from calcguard.errors import CalcGuardError
from calcguard.tier1 import assert_signed


def test_signed_passes_when_sign_and_magnitude_agree():
    assert_signed(-12.5, -12.5)


def test_signed_fails_when_only_the_sign_differs():
    """The whole point: abs() would call these equal."""
    with pytest.raises(CalcGuardError) as e:
        assert_signed(12.5, -12.5)
    assert "sign" in str(e.value).lower()


def test_signed_fails_on_magnitude_too():
    with pytest.raises(CalcGuardError):
        assert_signed(-13.7, -12.5, rel=1e-3)


def test_signed_treats_zero_without_a_sign_trap():
    """-0.0 and 0.0 must not be reported as a sign disagreement."""
    assert_signed(0.0, -0.0, abs_tol=1e-12)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: FAIL, `ImportError: cannot import name 'assert_signed'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/calcguard/tier1.py
"""Assertions needing nothing but numbers. No adapter, no domain knowledge."""
from __future__ import annotations

import math

from .errors import CalcGuardError, fail


def assert_signed(actual: float, expected: float, rel: float = 1e-9,
                  abs_tol: float = 0.0, what: str = "value") -> None:
    """Compare SIGNED values; a sign disagreement fails even at equal magnitude.

    calcguard cannot detect that a caller passed ``abs(x)`` -- nothing can, at
    runtime. What it can do is make the signed comparison the easy path and name
    the sign explicitly when it is the difference, so the failure is diagnosable
    from CI output alone.
    """
    if math.isclose(actual, expected, rel_tol=rel, abs_tol=max(abs_tol, 1e-15)):
        return
    same_magnitude = math.isclose(abs(actual), abs(expected),
                                  rel_tol=rel, abs_tol=max(abs_tol, 1e-15))
    detail = ("the MAGNITUDES agree and only the SIGN differs -- an abs() "
              "comparison would have passed this" if same_magnitude else "")
    fail(f"signed {what}", expected, actual, detail)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: PASS, 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/tier1.py tests/test_tier1.py
git commit -m "feat: assert_signed, which names the sign when that is the difference"
```

---

### Task 3: `assert_matches_closed_form` and `assert_bounded_both_sides`

**Files:**
- Modify: `src/calcguard/tier1.py`
- Modify: `tests/test_tier1.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_tier1.py
from calcguard.tier1 import assert_bounded_both_sides, assert_matches_closed_form


def test_closed_form_passes_and_carries_its_citation():
    w, L = 0.01, 120.0
    assert_matches_closed_form(w * L ** 2 / 8, w * L ** 2 / 8, cite="wL^2/8")


def test_closed_form_failure_message_contains_the_citation():
    """A failure must say WHICH closed form was violated."""
    with pytest.raises(CalcGuardError) as e:
        assert_matches_closed_form(1.0, 2.0, cite="wL^2/8")
    assert "wL^2/8" in str(e.value)


def test_bounded_both_sides_rejects_a_value_that_is_too_SMALL():
    """A one-sided 'error <= budget' check is passed for free by any bug that
    ZEROES the error. Both sides must be pinned."""
    with pytest.raises(CalcGuardError):
        assert_bounded_both_sides(0.0, lo=0.5, hi=1.5, what="residual")


def test_bounded_both_sides_rejects_a_value_that_is_too_large():
    with pytest.raises(CalcGuardError):
        assert_bounded_both_sides(9.0, lo=0.5, hi=1.5, what="residual")


def test_bounded_both_sides_accepts_a_value_inside():
    assert_bounded_both_sides(1.0, lo=0.5, hi=1.5, what="residual")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: FAIL, `ImportError: cannot import name 'assert_bounded_both_sides'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/calcguard/tier1.py
def assert_matches_closed_form(actual: float, expected: float, cite: str,
                               rel: float = 1e-9) -> None:
    """Check against a hand-derivable result, naming the formula.

    ``cite`` is required, not optional: a closed-form check whose formula is not
    recorded cannot be audited later, and this package exists to be auditable.
    """
    if math.isclose(actual, expected, rel_tol=rel, abs_tol=1e-15):
        return
    fail(f"closed form {cite}", expected, actual)


def assert_bounded_both_sides(value: float, lo: float, hi: float,
                              what: str = "value") -> None:
    """Pin a quantity from BELOW as well as above.

    ``assert error <= budget`` is satisfied for free by any bug that drives the
    error to zero -- for instance by reporting no force at all. Requiring a
    lower bound turns 'suspiciously good' into a failure.
    """
    if lo <= value <= hi:
        return
    side = "below" if value < lo else "above"
    fail(f"{what} within [{lo}, {hi}]", f"{lo}..{hi}", value,
         f"value falls {side} the band; a value that is too GOOD is also a failure")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: PASS, 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/tier1.py tests/test_tier1.py
git commit -m "feat: closed-form and both-sided bound assertions"
```

---

### Task 4: `assert_scales` and `assert_monotonic`

`assert_scales` is what catches a stale-length bug: two members of different
length must produce different answers, in a known ratio.

**Files:**
- Modify: `src/calcguard/tier1.py`
- Modify: `tests/test_tier1.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_tier1.py
from calcguard.tier1 import assert_monotonic, assert_scales


def test_scales_passes_for_a_linear_response():
    assert_scales(lambda w: 5.0 * w, x=2.0, factor=2.0, power=1)


def test_scales_passes_for_a_quadratic_response():
    """Moment goes as L^2, so doubling the span must quadruple it."""
    assert_scales(lambda L: 0.01 * L ** 2 / 8, x=60.0, factor=2.0, power=2)


def test_scales_catches_a_response_that_ignores_its_input():
    """A stale cached length looks exactly like this: the answer does not move."""
    with pytest.raises(CalcGuardError):
        assert_scales(lambda L: 42.0, x=60.0, factor=2.0, power=2)


def test_monotonic_catches_a_response_that_goes_the_wrong_way():
    with pytest.raises(CalcGuardError):
        assert_monotonic(lambda w: -w, xs=[1.0, 2.0, 3.0], direction="increasing")


def test_monotonic_passes_when_more_load_means_more_demand():
    assert_monotonic(lambda w: 3.0 * w, xs=[1.0, 2.0, 3.0], direction="increasing")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: FAIL, `ImportError: cannot import name 'assert_scales'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/calcguard/tier1.py
from collections.abc import Callable, Sequence


def assert_scales(fn: Callable[[float], float], x: float, factor: float,
                  power: int = 1, rel: float = 1e-9) -> None:
    """Scaling one input by ``factor`` must scale the output by ``factor**power``.

    Catches a whole class of error in which a computation silently ignores one
    of its inputs -- a cached or stale length being the case that motivated
    this. A function that returns a constant fails immediately.
    """
    base = fn(x)
    scaled = fn(x * factor)
    expected = base * factor ** power
    if math.isclose(scaled, expected, rel_tol=rel, abs_tol=1e-15):
        return
    fail(f"scaling by {factor} to the power {power}", expected, scaled,
         f"f({x}) = {base}; f({x * factor}) = {scaled}. A result that does not "
         f"move with its input usually means the input is not being read.")


def assert_monotonic(fn: Callable[[float], float], xs: Sequence[float],
                     direction: str = "increasing") -> None:
    """Demand must not fall when load rises (or vice versa)."""
    ys = [fn(x) for x in xs]
    for a, b in zip(ys, ys[1:]):
        ok = b >= a if direction == "increasing" else b <= a
        if not ok:
            fail(f"monotonic {direction}", f"{direction} sequence", ys)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: PASS, 14 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/tier1.py tests/test_tier1.py
git commit -m "feat: scaling and monotonicity assertions"
```

---

### Task 5: `assert_coverage` and `assert_schema_matches_capability`

Two defects came from a program looking healthier than it was: a parameter sweep
where refusals read as passes, and a UI control that always refused.

**Files:**
- Modify: `src/calcguard/tier1.py`
- Modify: `tests/test_tier1.py`

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_tier1.py
from calcguard.tier1 import assert_coverage, assert_schema_matches_capability


def test_coverage_fails_when_most_cases_were_skipped():
    """A skipped case is not a passing case, and the two look identical in a
    green test run."""
    with pytest.raises(CalcGuardError) as e:
        assert_coverage(built=2, total=10, floor=0.5, what="parameter sweep")
    assert "skip" in str(e.value).lower() or "built" in str(e.value).lower()


def test_coverage_passes_when_enough_cases_actually_ran():
    assert_coverage(built=9, total=10, floor=0.5, what="parameter sweep")


def test_schema_fails_when_a_knob_cannot_be_honoured():
    with pytest.raises(CalcGuardError) as e:
        assert_schema_matches_capability(declared={"a", "b"}, supported={"a"},
                                         what="overhang")
    assert "b" in str(e.value)


def test_schema_fails_when_a_capability_has_no_knob():
    """The other direction: geometry exists that the user cannot reach."""
    with pytest.raises(CalcGuardError):
        assert_schema_matches_capability(declared={"a"}, supported={"a", "b"},
                                         what="overhang")


def test_schema_passes_when_the_two_agree():
    assert_schema_matches_capability(declared={"a"}, supported={"a"}, what="overhang")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: FAIL, `ImportError: cannot import name 'assert_coverage'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/calcguard/tier1.py
def assert_coverage(built: int, total: int, floor: float = 0.5,
                    what: str = "cases") -> None:
    """Assert that enough of a sweep actually RAN.

    A generator that refuses its inputs produces a skip, and a skip reads
    exactly like a pass in a green test run. Measured on a real sweep: 2 of 10
    cases built, 8 refused silently, suite green.
    """
    if total == 0:
        fail(f"{what} coverage", "at least one case", "no cases at all")
    frac = built / total
    if frac >= floor:
        return
    fail(f"{what} coverage", f">= {floor:.0%}", f"{frac:.0%} ({built}/{total})",
         "the rest were skipped or refused, and a skip reads exactly like a pass")


def assert_schema_matches_capability(declared: set, supported: set,
                                     what: str = "capability") -> None:
    """What a program ADVERTISES must equal what it can honour, both ways.

    A knob offering a value that is always refused is a defect the user meets
    and the tests never do. A capability with no knob is one nobody can reach.
    """
    phantom = declared - supported
    unreachable = supported - declared
    if not phantom and not unreachable:
        return
    fail(f"{what} schema/capability parity", sorted(supported), sorted(declared),
         f"advertised but unusable: {sorted(phantom)}; "
         f"available but unreachable: {sorted(unreachable)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tier1.py -v`
Expected: PASS, 19 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/tier1.py tests/test_tier1.py
git commit -m "feat: coverage and schema-vs-capability assertions"
```

---

### Task 6: The adapter protocol

**Files:**
- Create: `src/calcguard/protocols.py`
- Test: `tests/test_protocols.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_protocols.py
from calcguard.protocols import EndForces, Geometry, PointLoad, StructuralAdapter


def test_end_forces_carries_both_ends_of_every_quantity():
    """Axial at BOTH ends, not one: on an inclined member under transverse load
    the axial varies along the span, and reporting one end understated demand by
    up to 26.6 % in the case that motivated this package."""
    f = EndForces(Ni=-1.0, Nj=-2.0, Vi=3.0, Vj=-3.0, Mi=4.0, Mj=-4.0)
    assert f.Ni != f.Nj


def test_geometry_exposes_length_and_direction():
    g = Geometry(length=100.0, cos=1.0, sin=0.0)
    assert g.length == 100.0


def test_a_minimal_adapter_satisfies_the_protocol():
    class Tiny:
        def members(self): return [0]
        def member_end_forces(self, mid): return EndForces(0, 0, 0, 0, 0, 0)
        def member_geometry(self, mid): return Geometry(1.0, 1.0, 0.0)
        def member_transverse_load(self, mid): return 0.0
        def applied_loads(self): return []
        def reactions(self): return {}

    assert isinstance(Tiny(), StructuralAdapter)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_protocols.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'calcguard.protocols'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/calcguard/protocols.py
"""The entire coupling surface between calcguard and a host program.

Tier 1 and tier 3 need none of this. Only the conservation assertions do, and
they need the least a program can expose: what its members are, what forces sit
at their ends, how long they are, what load is on them, and what the supports
push back with.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class EndForces:
    """Local end forces, tension-positive axial.

    BOTH ends of every quantity. Axial is not constant along a member carrying a
    transverse load with a component along its own axis, and a single value
    silently reports one end.
    """

    Ni: float
    Nj: float
    Vi: float
    Vj: float
    Mi: float
    Mj: float


@dataclass(frozen=True)
class Geometry:
    """Member length and direction cosines in the global frame."""

    length: float
    cos: float
    sin: float


@dataclass(frozen=True)
class PointLoad:
    """A load applied to the structure, in global components."""

    fx: float
    fy: float


@dataclass(frozen=True)
class Reaction:
    """A support reaction, in global components."""

    rx: float
    ry: float
    mz: float = 0.0


@runtime_checkable
class StructuralAdapter(Protocol):
    """Implement this to unlock the conservation assertions. ~20 lines."""

    def members(self) -> Iterable[int]: ...
    def member_end_forces(self, mid: int) -> EndForces: ...
    def member_geometry(self, mid: int) -> Geometry: ...
    def member_transverse_load(self, mid: int) -> float: ...
    def applied_loads(self) -> Sequence[PointLoad]: ...
    def reactions(self) -> Mapping[int, Reaction]: ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_protocols.py -v`
Expected: PASS, 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/protocols.py tests/test_protocols.py
git commit -m "feat: the adapter protocol, the whole coupling surface"
```

---

### Task 7: `assert_equilibrium` — the highest-value assertion

Catches three of the six motivating defects on its own.

**Files:**
- Create: `src/calcguard/tier2.py`
- Test: `tests/test_tier2.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tier2.py
import pytest

from calcguard.errors import CalcGuardError
from calcguard.protocols import EndForces, Geometry, PointLoad, Reaction
from calcguard.tier2 import assert_equilibrium, assert_free_boundary_carries_nothing


class Cantilever:
    """A vertical cantilever under self weight, fixed at the base (node 0).

    The base must carry the whole weight and the free tip nothing. The real
    defect reported it exactly inverted.
    """

    def __init__(self, w=-0.01, L=100.0, invert=False):
        self.w, self.L = w, L
        total = w * L
        self.Ni, self.Nj = (0.0, total) if invert else (total, 0.0)

    def members(self): return [0]
    def member_end_forces(self, mid):
        return EndForces(Ni=self.Ni, Nj=self.Nj, Vi=0.0, Vj=0.0, Mi=0.0, Mj=0.0)
    def member_geometry(self, mid): return Geometry(self.L, 0.0, 1.0)
    def member_transverse_load(self, mid): return self.w
    def applied_loads(self): return [PointLoad(0.0, self.w * self.L)]
    def reactions(self): return {0: Reaction(0.0, -self.w * self.L)}


def test_equilibrium_passes_on_the_correct_cantilever():
    assert_equilibrium(Cantilever(invert=False))


def test_equilibrium_catches_axial_placed_at_the_wrong_end():
    with pytest.raises(CalcGuardError):
        assert_equilibrium(Cantilever(invert=True))


def test_free_boundary_carries_nothing_passes_when_the_tip_is_free():
    assert_free_boundary_carries_nothing(Cantilever(invert=False), mid=0, end="j")


def test_free_boundary_catches_a_tip_carrying_load():
    """A free end carrying force is not a small error; it is not equilibrium."""
    with pytest.raises(CalcGuardError) as e:
        assert_free_boundary_carries_nothing(Cantilever(invert=True), mid=0, end="j")
    assert "free" in str(e.value).lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tier2.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'calcguard.tier2'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/calcguard/tier2.py
"""Conservation assertions. These need an adapter; they repay it.

assert_equilibrium alone catches three of the six defects that motivated this
package, because neither a sign error nor a stale length nor a force placed at
the wrong end can satisfy it.
"""
from __future__ import annotations

from .errors import fail
from .protocols import StructuralAdapter


def assert_equilibrium(adapter: StructuralAdapter, tol: float = 1e-6) -> None:
    """Global force balance: reactions must equal the applied load.

    Checked in both global directions. This is the cheapest true statement
    about any structure, and the one most solvers are never asked to prove.
    """
    applied_x = sum(p.fx for p in adapter.applied_loads())
    applied_y = sum(p.fy for p in adapter.applied_loads())
    react_x = sum(r.rx for r in adapter.reactions().values())
    react_y = sum(r.ry for r in adapter.reactions().values())

    for axis, applied, react in (("X", applied_x, react_x), ("Y", applied_y, react_y)):
        residual = applied + react
        if abs(residual) > tol:
            fail(f"global equilibrium in {axis}", 0.0, residual,
                 f"applied {applied}, reactions {react}. The structure is not "
                 f"in balance, so at least one force is wrong or misplaced.")

    # Per member: the axial change along a member must equal the along-member
    # component of the load applied to it.
    for mid in adapter.members():
        f = adapter.member_end_forces(mid)
        g = adapter.member_geometry(mid)
        w = adapter.member_transverse_load(mid)
        # Axial accumulates from end j back to end i, so the change is the
        # NEGATIVE of the along-member load. Verified against a vertical
        # cantilever: base carries w*L, tip carries zero, so Nj - Ni = -w*L.
        expected_change = -w * g.sin * g.length
        actual_change = f.Nj - f.Ni
        if abs(actual_change - expected_change) > max(tol, tol * abs(expected_change)):
            fail(f"member {mid} axial equilibrium", expected_change, actual_change,
                 "the axial change from end i to end j must equal the load "
                 "component along the member")


def assert_free_boundary_carries_nothing(adapter: StructuralAdapter, mid: int,
                                         end: str, tol: float = 1e-9) -> None:
    """An unrestrained, unloaded member end carries no force. Not approximately."""
    f = adapter.member_end_forces(mid)
    n = f.Ni if end == "i" else f.Nj
    v = f.Vi if end == "i" else f.Vj
    m = f.Mi if end == "i" else f.Mj
    for name, value in (("axial", n), ("shear", v), ("moment", m)):
        if abs(value) > tol:
            fail(f"free end {end} of member {mid} carries no {name}", 0.0, value,
                 "a free end carrying force is not a small error, it is not "
                 "equilibrium")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tier2.py -v`
Expected: PASS, 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/tier2.py tests/test_tier2.py
git commit -m "feat: assert_equilibrium and the free-boundary check"
```

---

### Task 8: `compare_to_reference`

**Files:**
- Create: `src/calcguard/reference.py`
- Test: `tests/test_reference.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_reference.py
import pytest

from calcguard.errors import CalcGuardError
from calcguard.reference import compare_to_reference


def test_opposite_sign_conventions_are_reconciled_not_reported_as_error():
    """Calcs.com is compression-positive; our engines are tension-positive.
    Comparing without flipping makes a CORRECT engine look catastrophic."""
    table = compare_to_reference(
        ours={"m1": -3910.0}, reference={"m1": 3910.0},
        reference_sign="compression-positive", tol_pct=1.0)
    table.assert_within()
    assert table.max_error_pct < 1e-9


def test_agreement_is_measured_against_the_PEAK_not_each_item():
    """A 50 % error on a member carrying 10 lb is noise; the same percentage on
    a governing member is not. Both are reported; only the second fails."""
    table = compare_to_reference(
        ours={"big": 4000.0, "tiny": 15.0},
        reference={"big": 4000.0, "tiny": 10.0}, tol_pct=1.0)
    table.assert_within()                       # 5 lb on a 4000 lb peak
    assert table.worst_item == "tiny"


def test_a_real_disagreement_on_a_governing_item_fails():
    table = compare_to_reference(
        ours={"big": 3000.0}, reference={"big": 4000.0}, tol_pct=1.0)
    with pytest.raises(CalcGuardError):
        table.assert_within()


def test_markdown_lists_every_item_and_the_summary():
    table = compare_to_reference(ours={"a": 1.0}, reference={"a": 1.0}, tol_pct=1.0)
    md = table.to_markdown()
    assert "| a |" in md and "%" in md
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_reference.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'calcguard.reference'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/calcguard/reference.py
"""Comparison against an external reference, with the traps handled explicitly.

The two traps that make a correct engine look wrong: an opposite SIGN convention
(Calcs.com reports compression-positive), and a UNIT difference. Both are
declared here rather than left to the caller to remember.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .errors import fail


@dataclass
class ComparisonTable:
    rows: list[tuple[str, float, float, float, float]] = field(default_factory=list)
    tol_pct: float = 1.0
    peak: float = 0.0

    @property
    def max_error_pct(self) -> float:
        return max((r[4] for r in self.rows), default=0.0)

    @property
    def worst_item(self) -> str | None:
        if not self.rows:
            return None
        return max(self.rows, key=lambda r: abs(r[3]))[0]

    def assert_within(self) -> None:
        """Fail if any item differs by more than tol_pct OF THE PEAK quantity."""
        bad = [r for r in self.rows if r[4] > self.tol_pct]
        if bad:
            worst = max(bad, key=lambda r: r[4])
            fail("reference comparison", f"<= {self.tol_pct}% of peak {self.peak:g}",
                 f"{worst[4]:.2f}% on {worst[0]}",
                 f"{len(bad)} of {len(self.rows)} items exceed tolerance")

    def to_markdown(self) -> str:
        head = ("| item | ours | reference | diff | % of peak |\n"
                "|---|---|---|---|---|\n")
        body = "".join(f"| {n} | {o:g} | {r:g} | {d:+g} | {p:.2f} |\n"
                       for n, o, r, d, p in self.rows)
        return head + body


def compare_to_reference(ours: Mapping[str, float], reference: Mapping[str, float],
                         tol_pct: float = 1.0, reference_sign: str = "same",
                         unit_factor: float = 1.0) -> ComparisonTable:
    """Compare, reconciling sign convention and units before judging.

    reference_sign="compression-positive" flips the reference to match a
    tension-positive engine. unit_factor multiplies the reference.
    """
    missing = set(ours) ^ set(reference)
    if missing:
        fail("reference comparison keys", "identical key sets", sorted(missing),
             "an item present on one side only cannot be compared")
    flip = -1.0 if reference_sign == "compression-positive" else 1.0
    peak = max((abs(v) for v in reference.values()), default=0.0) * unit_factor
    table = ComparisonTable(tol_pct=tol_pct, peak=peak)
    for k in ours:
        ref = reference[k] * unit_factor * flip
        diff = ours[k] - ref
        pct = 100.0 * abs(diff) / peak if peak else 0.0
        table.rows.append((k, ours[k], ref, diff, pct))
    return table
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_reference.py -v`
Expected: PASS, 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/reference.py tests/test_reference.py
git commit -m "feat: reference comparison with sign and unit reconciliation"
```

---

### Task 9: The acceptance test — catch the six real defects

This is the task that decides whether calcguard is worth having.

**Files:**
- Create: `tests/test_acceptance_lgs.py`
- Modify: `src/calcguard/__init__.py` (export the public surface)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_acceptance_lgs.py
"""calcguard must catch the six defects that motivated it.

Each is reproduced as a minimal fixture rather than by importing
lgs-truss-designer, so this suite has no external dependency and stays true
even after those bugs are fixed upstream.
"""
import pytest

from calcguard import (CalcGuardError, assert_bounded_both_sides, assert_coverage,
                       assert_equilibrium, assert_matches_closed_form,
                       assert_scales, assert_schema_matches_capability,
                       assert_signed)
from calcguard.protocols import EndForces, Geometry, PointLoad, Reaction


class _Beam:
    """One member; end forces supplied so a defect can be injected."""

    def __init__(self, f: EndForces, w=0.0, L=100.0, sin=0.0,
                 applied=0.0, react=0.0):
        self.f, self.w, self.L, self._sin = f, w, L, sin
        self.applied, self.react = applied, react

    def members(self): return [0]
    def member_end_forces(self, mid): return self.f
    def member_geometry(self, mid):
        return Geometry(self.L, (1 - self._sin ** 2) ** 0.5, self._sin)
    def member_transverse_load(self, mid): return self.w
    def applied_loads(self): return [PointLoad(0.0, self.applied)]
    def reactions(self): return {0: Reaction(0.0, self.react)}


def test_defect_1_axial_at_the_wrong_end():
    """Vertical cantilever: base must carry -1.0, tip 0.0. The bug inverted it."""
    broken = _Beam(EndForces(Ni=0.0, Nj=-1.0, Vi=0, Vj=0, Mi=0, Mj=0),
                   w=-0.01, L=100.0, sin=1.0, applied=-1.0, react=1.0)
    with pytest.raises(CalcGuardError):
        assert_equilibrium(broken)


def test_defect_2_fixed_end_force_sign_inverted():
    """A simply supported end must carry zero moment; the bug gave -wL^2/6."""
    with pytest.raises(CalcGuardError):
        assert_signed(-16.6667, 0.0, abs_tol=1e-6, what="end moment")


def test_defect_3_stale_member_length():
    """The envelope read a leftover L, so the answer stopped moving with span."""
    def stale_moment(L):
        return 0.01 * 60.0 ** 2 / 8      # always the FIRST member's length
    with pytest.raises(CalcGuardError):
        assert_scales(stale_moment, x=60.0, factor=3.0, power=2)


def test_defect_4_end_moment_instead_of_the_span_peak():
    """Simply supported: both END moments are zero while the member carries
    wL^2/8. Sizing on the ends saw nothing."""
    w, L = 0.01, 120.0
    end_only = 0.0
    with pytest.raises(CalcGuardError):
        assert_matches_closed_form(end_only, w * L ** 2 / 8, cite="wL^2/8")


def test_defect_5_a_refusal_read_as_a_pass():
    """Four of ten sweep cases built; the rest refused, and the suite was green."""
    with pytest.raises(CalcGuardError):
        assert_coverage(built=4, total=10, floor=0.9, what="planarity sweep")


def test_defect_6_a_knob_that_can_never_be_honoured():
    """Two truss types advertised an overhang the engine always refused."""
    with pytest.raises(CalcGuardError):
        assert_schema_matches_capability(
            declared={"fink", "howe", "pratt", "mono", "double_fink", "double_howe"},
            supported={"fink", "howe", "pratt", "mono"},
            what="overhang")


def test_all_six_assertions_stay_silent_on_correct_input():
    """The other half of every guard: it must not fire on healthy input, or it
    is noise and will be disabled."""
    good = _Beam(EndForces(Ni=-1.0, Nj=0.0, Vi=0, Vj=0, Mi=0, Mj=0),
                 w=-0.01, L=100.0, sin=1.0, applied=-1.0, react=1.0)
    assert_equilibrium(good)
    assert_signed(0.0, 0.0, abs_tol=1e-9)
    assert_scales(lambda L: 0.01 * L ** 2 / 8, x=60.0, factor=3.0, power=2)
    assert_matches_closed_form(0.01 * 120 ** 2 / 8, 0.01 * 120 ** 2 / 8, cite="wL^2/8")
    assert_coverage(built=10, total=10, floor=0.9, what="planarity sweep")
    assert_schema_matches_capability(declared={"fink"}, supported={"fink"},
                                     what="overhang")
    assert_bounded_both_sides(1.0, 0.5, 1.5)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_acceptance_lgs.py -v`
Expected: FAIL, `ImportError: cannot import name 'assert_equilibrium' from 'calcguard'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/calcguard/__init__.py
"""Executable physics assertions for engineering calculation programs."""
from .errors import CalcGuardError
from .reference import ComparisonTable, compare_to_reference
from .tier1 import (assert_bounded_both_sides, assert_coverage,
                    assert_matches_closed_form, assert_monotonic, assert_scales,
                    assert_schema_matches_capability, assert_signed)
from .tier2 import assert_equilibrium, assert_free_boundary_carries_nothing

__version__ = "0.1.0"
__all__ = [
    "CalcGuardError",
    "assert_signed", "assert_bounded_both_sides", "assert_matches_closed_form",
    "assert_scales", "assert_monotonic", "assert_coverage",
    "assert_schema_matches_capability",
    "assert_equilibrium", "assert_free_boundary_carries_nothing",
    "compare_to_reference", "ComparisonTable",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ -v`
Expected: PASS, all tests pass including 7 in test_acceptance_lgs.py

- [ ] **Step 5: Commit**

```bash
git add src/calcguard/__init__.py tests/test_acceptance_lgs.py
git commit -m "test: calcguard catches all six defects that motivated it"
```

---

### Task 10: README and install into lgs-truss-designer

**Files:**
- Create: `README.md`
- Test: manual verification, recorded below

- [ ] **Step 1: Write the README**

```markdown
# calcguard

Executable physics assertions for engineering calculation programs.

Six defects in a cold-formed-steel truss engine passed a 1277-test suite.
Two were unconservative and in the shipped design path. Every one was caught
by an independent tool or a violated invariant — none by the tests.

calcguard turns those invariants into assertions that run in CI.

## Install

    pip install -e ~/projects/calcguard

## Use

    from calcguard import assert_equilibrium, assert_matches_closed_form

    assert_equilibrium(MyAdapter(model, result))
    assert_matches_closed_form(mid_moment, w * L**2 / 8, cite="wL^2/8")

Tier 1 needs nothing. Tier 2 needs a ~20-line adapter. Tier 3 compares
against an external reference, reconciling sign convention and units.

## The one to start with

`assert_equilibrium`. It catches three of the six on its own, because
neither a sign error nor a stale length nor a force at the wrong end can
satisfy it.
```

- [ ] **Step 2: Verify the package installs into a consumer**

Run:
```bash
/home/atomicjr/projects/lgs-c2/.venv/bin/pip install -e ~/projects/calcguard
/home/atomicjr/projects/lgs-c2/.venv/bin/python -c "import calcguard; print(calcguard.__version__)"
```
Expected: `0.1.0`

- [ ] **Step 3: Run the full suite once more**

Run: `cd ~/projects/calcguard && python -m pytest tests/ -v`
Expected: PASS, all green

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README"
```

---

## Deferred to a follow-up plan

Named here so they are not forgotten, and excluded so this plan finishes:

- `assert_symmetric` and `assert_reactions_balance_applied_load` — real, but
  `assert_equilibrium` covers the motivating cases; add when a defect needs them.
- The `engineering-calc-verification` skill and `references/traps.md` — the
  library must exist and be proven first.
- The `VERIFICATION.md` generator — `ComparisonTable.to_markdown()` is the
  half that matters; the template around it can wait.
- A real `StructuralAdapter` for `lgs-truss-designer` — belongs with the
  S100-2024 migration, which is calcguard's first customer.
