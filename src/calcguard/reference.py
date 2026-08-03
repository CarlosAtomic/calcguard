"""Comparison against an external reference, with the traps handled explicitly.

The two traps that make a correct engine look wrong: an opposite SIGN convention
(Calcs.com reports compression-positive), and a UNIT difference. Both are
declared here rather than left to the caller to remember.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .errors import fail


@dataclass
class ComparisonTable:
    rows: list[tuple[str, float, float, float, float]] = field(default_factory=list)
    tol_pct: float = 1.0
    peak: float = 0.0

    @property
    def max_error_pct(self) -> float:
        return max((r[4] for r in self.rows), default=0.0)

    @property
    def worst_item(self) -> str | None:
        if not self.rows:
            return None
        return max(self.rows, key=lambda r: abs(r[3]))[0]

    def assert_within(self) -> None:
        """Fail if any item differs by more than tol_pct OF THE PEAK quantity."""
        bad = [r for r in self.rows if r[4] > self.tol_pct]
        if bad:
            worst = max(bad, key=lambda r: r[4])
            fail("reference comparison", f"<= {self.tol_pct}% of peak {self.peak:g}",
                 f"{worst[4]:.2f}% on {worst[0]}",
                 f"{len(bad)} of {len(self.rows)} items exceed tolerance")

    def to_markdown(self) -> str:
        head = ("| item | ours | reference | diff | % of peak |\n"
                "|---|---|---|---|---|\n")
        body = "".join(f"| {n} | {o:g} | {r:g} | {d:+g} | {p:.2f} |\n"
                       for n, o, r, d, p in self.rows)
        return head + body


def compare_to_reference(ours: Mapping[str, float], reference: Mapping[str, float],
                         tol_pct: float = 1.0, reference_sign: str = "same",
                         unit_factor: float = 1.0) -> ComparisonTable:
    """Compare, reconciling sign convention and units before judging.

    reference_sign="compression-positive" flips the reference to match a
    tension-positive engine. unit_factor multiplies the reference.
    """
    missing = set(ours) ^ set(reference)
    if missing:
        fail("reference comparison keys", "identical key sets", sorted(missing),
             "an item present on one side only cannot be compared")
    flip = -1.0 if reference_sign == "compression-positive" else 1.0
    peak = max((abs(v) for v in reference.values()), default=0.0) * unit_factor
    table = ComparisonTable(tol_pct=tol_pct, peak=peak)
    for k in ours:
        ref = reference[k] * unit_factor * flip
        diff = ours[k] - ref
        pct = 100.0 * abs(diff) / peak if peak else 0.0
        table.rows.append((k, ours[k], ref, diff, pct))
    return table
