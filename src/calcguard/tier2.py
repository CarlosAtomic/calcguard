"""Conservation assertions. These need an adapter; they repay it.

assert_equilibrium alone catches three of the six defects that motivated this
package, because neither a sign error nor a stale length nor a force placed at
the wrong end can satisfy it.
"""
from __future__ import annotations

from .errors import fail
from .protocols import StructuralAdapter


def assert_equilibrium(adapter: StructuralAdapter, tol: float = 1e-6) -> None:
    """Global force balance: reactions must equal the applied load.

    Checked in both global directions. This is the cheapest true statement
    about any structure, and the one most solvers are never asked to prove.
    """
    applied_x = sum(p.fx for p in adapter.applied_loads())
    applied_y = sum(p.fy for p in adapter.applied_loads())
    react_x = sum(r.rx for r in adapter.reactions().values())
    react_y = sum(r.ry for r in adapter.reactions().values())

    for axis, applied, react in (("X", applied_x, react_x), ("Y", applied_y, react_y)):
        residual = applied + react
        if abs(residual) > tol:
            fail(f"global equilibrium in {axis}", 0.0, residual,
                 f"applied {applied}, reactions {react}. The structure is not "
                 f"in balance, so at least one force is wrong or misplaced.")

    # Per member: the axial change along a member must equal the along-member
    # component of the load applied to it.
    for mid in adapter.members():
        f = adapter.member_end_forces(mid)
        g = adapter.member_geometry(mid)
        w = adapter.member_transverse_load(mid)
        # Axial accumulates from end j back to end i, so the change is the
        # NEGATIVE of the along-member load. Verified against a vertical
        # cantilever: base carries w*L, tip carries zero, so Nj - Ni = -w*L.
        expected_change = -w * g.sin * g.length
        actual_change = f.Nj - f.Ni
        if abs(actual_change - expected_change) > max(tol, tol * abs(expected_change)):
            fail(f"member {mid} axial equilibrium", expected_change, actual_change,
                 "the axial change from end i to end j must equal the load "
                 "component along the member")


def assert_free_boundary_carries_nothing(adapter: StructuralAdapter, mid: int,
                                         end: str, tol: float = 1e-9) -> None:
    """An unrestrained, unloaded member end carries no force. Not approximately."""
    f = adapter.member_end_forces(mid)
    n = f.Ni if end == "i" else f.Nj
    v = f.Vi if end == "i" else f.Vj
    m = f.Mi if end == "i" else f.Mj
    for name, value in (("axial", n), ("shear", v), ("moment", m)):
        if abs(value) > tol:
            fail(f"free end {end} of member {mid} carries no {name}", 0.0, value,
                 "a free end carrying force is not a small error, it is not "
                 "equilibrium")
