"""Invariants that fire in a shipped engine, not only in a test run.

The tier1 and tier2 assertions are test-shaped in two ways that matter here. They
raise ``CalcGuardError``, which subclasses ``AssertionError`` so pytest reports a
failure rather than an error -- deliberate for tests, wrong for a running program,
where callers catch ``ValueError`` and an ``AssertionError`` reaching an API is a
crash rather than a refusal. And several of them probe a *function* across many
inputs, which a solver cannot do inline.

So a physics invariant that only ever ran in tests only ever guarded the fixtures
somebody thought to write. This tier guards the number actually produced, on the
input actually given, including the inputs nobody anticipated.
"""
import math

from .errors import CalcGuardError


def require_within(value, lo, hi, *, what, cite, error=CalcGuardError):
    """Refuse unless ``lo <= value <= hi``. Returns None when the value is sound.

    ``error`` is the exception type to raise, so an engine keeps its own refusal
    vocabulary instead of leaking an AssertionError to its callers. It defaults to
    ``CalcGuardError`` for use in tests.

    Both bounds are required. ``value <= hi`` alone is satisfied for free by any
    bug that drives the quantity to zero, so a value that is too good fails too.

    A non-finite value is refused before the comparison. NaN compares False against
    every bound, so which branch it lands in is an accident of how the check was
    written, and infinity slips through any bound expressed as ``float("inf")``.
    """
    if not math.isfinite(value):
        raise error(
            f"{what} must be finite and within [{lo}, {hi}]: measured {value!r}"
            f"\n  cite: {cite}"
            f"\n  a non-finite value is not a measurement; it is the absence of one"
        )
    if lo <= value <= hi:
        return None
    side = "below" if value < lo else "above"
    raise error(
        f"{what} outside [{lo}, {hi}]: measured {value!r}"
        f"\n  cite: {cite}"
        f"\n  value falls {side} the band; a value that is too GOOD is also a failure"
    )
