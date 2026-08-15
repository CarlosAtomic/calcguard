"""Structural guard between the acceptance fixtures and the signal list.

Semantics are checked by the replay in the plan's Task 10; this file checks
only that the two documents have not drifted apart -- a signal renumbered,
a case orphaned, a signal added with no fixture behind it.
"""
import re
from pathlib import Path

SKILL = Path(__file__).parent.parent / "skills" / "engineering-judgment"
FORKS = SKILL / "acceptance" / "forks.md"
SIGNALS = SKILL / "references" / "fork-signals.md"

# Signals with no fixture on file yet. Explicit so the gap is visible in the
# test rather than absent from it. Removing a signal from here requires adding
# its case to forks.md.
SIGNALS_WITHOUT_RECEIPT: set[int] = set()


def _cases() -> dict[str, set[int]]:
    """Map case id -> expected signal ids, from forks.md."""
    text = FORKS.read_text()
    out: dict[str, set[int]] = {}
    current = None
    for line in text.splitlines():
        if m := re.match(r"^## ([A-Z]+-\d+)", line):
            current = m.group(1)
        elif m := re.match(r"^\*\*Expected signals:\*\* (.+)$", line):
            assert current, f"expected-signals line before any case heading: {line}"
            raw = m.group(1).strip()
            out[current] = set() if raw == "none" else {
                int(n) for n in re.findall(r"\d+", raw)
            }
            current = None
    return out


def _defined_signals() -> set[int]:
    """Signal ids defined in the fork-signals.md table."""
    return {
        int(m.group(1))
        for m in re.finditer(r"^\| (\d+) \|", SIGNALS.read_text(), re.M)
    }


def test_every_case_declares_expected_signals():
    cases = _cases()
    assert cases, "no acceptance cases parsed -- check the heading format"
    assert len(cases) == 10, f"expected 10 cases, parsed {sorted(cases)}"


def test_every_expected_signal_is_defined():
    defined = _defined_signals()
    assert defined, "no signals parsed -- check the table format in fork-signals.md"
    for case, expected in _cases().items():
        undefined = expected - defined
        assert not undefined, f"{case} expects undefined signal(s) {sorted(undefined)}"


def test_negative_control_trips_nothing():
    assert _cases()["CONTROL-1"] == set(), "the negative control must expect no signals"


def test_every_signal_has_a_fixture():
    exercised = set().union(*_cases().values())
    orphans = _defined_signals() - exercised - SIGNALS_WITHOUT_RECEIPT
    assert not orphans, (
        f"signal(s) {sorted(orphans)} have no acceptance case. Add one, or list "
        f"the id in SIGNALS_WITHOUT_RECEIPT so the gap stays visible."
    )
