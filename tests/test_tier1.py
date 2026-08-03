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
