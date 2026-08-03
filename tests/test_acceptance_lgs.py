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
