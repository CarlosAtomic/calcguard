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
