"""Tests for the runtime tier: invariants that fire in a shipped engine."""
import pytest

from calcguard import CalcGuardError, require_within


class Refusal(ValueError):
    """Stand-in for an engine's own refusal type."""


def test_a_value_inside_the_band_passes_silently():
    assert require_within(2.0, 0.0, 3.0, what="lambda/depth", cite="x") is None


def test_a_value_outside_the_band_raises_the_callers_error_type():
    # A shipped engine needs a DOMAIN refusal, not an AssertionError. Callers
    # catch ValueError; an AssertionError escaping to an API is a crash, not a
    # refusal, and `python -O` strips asserts outright.
    with pytest.raises(Refusal):
        require_within(4.5, 0.0, 3.0, what="lambda/depth", cite="x", error=Refusal)


def test_the_default_error_is_still_a_calcguard_error():
    with pytest.raises(CalcGuardError):
        require_within(4.5, 0.0, 3.0, what="lambda/depth", cite="x")


def test_the_message_names_the_invariant_the_bound_and_the_measurement():
    with pytest.raises(Refusal) as e:
        require_within(4.53, 0.0, 3.0, what="lambda/depth", cite="P0.18", error=Refusal)
    msg = str(e.value)
    assert "lambda/depth" in msg and "4.53" in msg and "3.0" in msg and "P0.18" in msg


def test_a_value_below_the_band_also_fails():
    # a quantity that is too GOOD is also a failure -- one-sided bounds are
    # satisfied for free by any bug that drives the value to zero
    with pytest.raises(Refusal):
        require_within(-1.0, 0.0, 3.0, what="pcrl", cite="x", error=Refusal)


def test_a_non_finite_value_fails_rather_than_comparing_false():
    # NaN compares False against every bound, so a naive `lo <= v <= hi` lets it
    # through as "outside" only by luck of the branch -- and inf silently passes
    # an upper bound written as float('inf')
    for bad in (float("nan"), float("inf")):
        with pytest.raises(Refusal):
            require_within(bad, 0.0, 3.0, what="pcrl", cite="x", error=Refusal)
