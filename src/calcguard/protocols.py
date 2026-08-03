"""The entire coupling surface between calcguard and a host program.

Tier 1 and tier 3 need none of this. Only the conservation assertions do, and
they need the least a program can expose: what its members are, what forces sit
at their ends, how long they are, what load is on them, and what the supports
push back with.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class EndForces:
    """Local end forces, tension-positive axial.

    BOTH ends of every quantity. Axial is not constant along a member carrying a
    transverse load with a component along its own axis, and a single value
    silently reports one end.
    """

    Ni: float
    Nj: float
    Vi: float
    Vj: float
    Mi: float
    Mj: float


@dataclass(frozen=True)
class Geometry:
    """Member length and direction cosines in the global frame."""

    length: float
    cos: float
    sin: float


@dataclass(frozen=True)
class PointLoad:
    """A load applied to the structure, in global components."""

    fx: float
    fy: float


@dataclass(frozen=True)
class Reaction:
    """A support reaction, in global components."""

    rx: float
    ry: float
    mz: float = 0.0


@runtime_checkable
class StructuralAdapter(Protocol):
    """Implement this to unlock the conservation assertions. ~20 lines."""

    def members(self) -> Iterable[int]: ...
    def member_end_forces(self, mid: int) -> EndForces: ...
    def member_geometry(self, mid: int) -> Geometry: ...
    def member_transverse_load(self, mid: int) -> float: ...
    def applied_loads(self) -> Sequence[PointLoad]: ...
    def reactions(self) -> Mapping[int, Reaction]: ...
