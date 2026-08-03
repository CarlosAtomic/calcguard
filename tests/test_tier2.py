import pytest

from calcguard.errors import CalcGuardError
from calcguard.protocols import EndForces, Geometry, PointLoad, Reaction
from calcguard.tier2 import assert_equilibrium, assert_free_boundary_carries_nothing


class Cantilever:
    """A vertical cantilever under self weight, fixed at the base (node 0).

    The base must carry the whole weight and the free tip nothing. The real
    defect reported it exactly inverted.
    """

    def __init__(self, w=-0.01, L=100.0, invert=False):
        self.w, self.L = w, L
        total = w * L
        self.Ni, self.Nj = (0.0, total) if invert else (total, 0.0)

    def members(self): return [0]
    def member_end_forces(self, mid):
        return EndForces(Ni=self.Ni, Nj=self.Nj, Vi=0.0, Vj=0.0, Mi=0.0, Mj=0.0)
    def member_geometry(self, mid): return Geometry(self.L, 0.0, 1.0)
    def member_transverse_load(self, mid): return self.w
    def applied_loads(self): return [PointLoad(0.0, self.w * self.L)]
    def reactions(self): return {0: Reaction(0.0, -self.w * self.L)}


def test_equilibrium_passes_on_the_correct_cantilever():
    assert_equilibrium(Cantilever(invert=False))


def test_equilibrium_catches_axial_placed_at_the_wrong_end():
    with pytest.raises(CalcGuardError):
        assert_equilibrium(Cantilever(invert=True))


def test_free_boundary_carries_nothing_passes_when_the_tip_is_free():
    assert_free_boundary_carries_nothing(Cantilever(invert=False), mid=0, end="j")


def test_free_boundary_catches_a_tip_carrying_load():
    """A free end carrying force is not a small error; it is not equilibrium."""
    with pytest.raises(CalcGuardError) as e:
        assert_free_boundary_carries_nothing(Cantilever(invert=True), mid=0, end="j")
    assert "free" in str(e.value).lower()
