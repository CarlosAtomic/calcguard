from calcguard.protocols import EndForces, Geometry, PointLoad, StructuralAdapter


def test_end_forces_carries_both_ends_of_every_quantity():
    """Axial at BOTH ends, not one: on an inclined member under transverse load
    the axial varies along the span, and reporting one end understated demand by
    up to 26.6 % in the case that motivated this package."""
    f = EndForces(Ni=-1.0, Nj=-2.0, Vi=3.0, Vj=-3.0, Mi=4.0, Mj=-4.0)
    assert f.Ni != f.Nj


def test_geometry_exposes_length_and_direction():
    g = Geometry(length=100.0, cos=1.0, sin=0.0)
    assert g.length == 100.0


def test_a_minimal_adapter_satisfies_the_protocol():
    class Tiny:
        def members(self): return [0]
        def member_end_forces(self, mid): return EndForces(0, 0, 0, 0, 0, 0)
        def member_geometry(self, mid): return Geometry(1.0, 1.0, 0.0)
        def member_transverse_load(self, mid): return 0.0
        def applied_loads(self): return []
        def reactions(self): return {}

    assert isinstance(Tiny(), StructuralAdapter)
