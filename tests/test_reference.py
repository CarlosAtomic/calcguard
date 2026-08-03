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
