"""Assertions needing nothing but numbers. No adapter, no domain knowledge."""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence

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
