"""Executable physics assertions for engineering calculation programs."""
from .errors import CalcGuardError
from .reference import ComparisonTable, compare_to_reference
from .runtime import require_within
from .tier1 import (assert_bounded_both_sides, assert_coverage,
                    assert_matches_closed_form, assert_monotonic, assert_scales,
                    assert_schema_matches_capability, assert_signed)
from .tier2 import assert_equilibrium, assert_free_boundary_carries_nothing

__version__ = "0.1.0"
__all__ = [
    "CalcGuardError",
    "assert_signed", "assert_bounded_both_sides", "assert_matches_closed_form",
    "assert_scales", "assert_monotonic", "assert_coverage",
    "assert_schema_matches_capability",
    "assert_equilibrium", "assert_free_boundary_carries_nothing",
    "compare_to_reference", "ComparisonTable",
    "require_within",
]
