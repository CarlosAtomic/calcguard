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
