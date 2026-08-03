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
