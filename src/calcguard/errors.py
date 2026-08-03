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
