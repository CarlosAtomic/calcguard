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


# ---------------------------------------------------------------------------
# Coverage labelling. These do not fail on a gap -- they make the gap visible.
# A suite that implies uniform confidence it does not have is worse than one
# that admits the hole.
# ---------------------------------------------------------------------------
import importlib.util

REPLAY = SKILL / "acceptance" / "replay.py"


def _replay_module():
    spec = importlib.util.spec_from_file_location("replay", REPLAY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_replay_strips_the_receipt_column():
    """The withholding rule must live in code, not in whoever runs it.

    Each receipt names the very clause its fixture describes -- signal 1's is
    "J3.4 -> Appendix A" and FORK-3's context names J3.4. Handed the full
    table, a scorer matches clause strings and the suite passes for the wrong
    reason.
    """
    table = _replay_module().signals_prompt_table()
    assert "Receipt" not in table
    assert "Appendix A" not in table
    assert "Whitmore" not in table
    assert "1.43" not in table
    # but the signals themselves must survive
    assert "Cross-reference body" in table
    assert table.count("\n|") >= 9


def test_every_signal_carries_an_evidence_label():
    """REAL / SYNTHETIC-ONLY / UNSCORED -- one per signal, no silent gaps."""
    cov = _replay_module().coverage()
    assert set(cov) == _defined_signals(), "every defined signal needs a label"
    allowed = {"REAL", "SYNTHETIC-ONLY", "UNSCORED"}
    assert set(cov.values()) <= allowed, f"unexpected labels: {set(cov.values()) - allowed}"


def test_real_records_are_referenced_not_copied():
    """Records are cited by path so a record edit cannot drift from its fixture."""
    for path, signals in _replay_module().real_records():
        assert path.exists(), f"real-record fixture points at a missing file: {path}"
        assert signals, f"{path.name} declares no signals"


# ---------------------------------------------------------------------------
# Real-record regression. Opt-in: needs a local model, so it is gated behind
# EJ_REGRESSION=1 rather than slowing the fast suite. Run it on EVERY signal
# edit -- that is when it earns its keep, because it says whether a judgment
# already made and pinned in code just became unsupported.
#
#   EJ_REGRESSION=1 .venv/bin/python -m pytest tests/test_skill_acceptance.py -k regression -v
# ---------------------------------------------------------------------------
import os

import pytest


@pytest.mark.skipif(os.environ.get("EJ_REGRESSION") != "1",
                    reason="set EJ_REGRESSION=1 (needs Ollama and a local model)")
def test_regression_recorded_signals_still_fire():
    r = _replay_module()
    if not r.ollama_up():
        pytest.skip("Ollama unreachable -- skipped, never a false green")
    model = os.environ.get("EJ_REGRESSION_MODEL", "deepseek-r1:32b")
    records = r.record_forks()
    assert records, "no JR-* records found to regress against"
    broken = []
    for path, recorded, fork in records:
        got = r.score(model, fork)
        if got is None:
            pytest.skip(f"model call failed on {path.name} -- unscored, not passed")
        if not recorded <= got:
            broken.append(f"{path.name}: recorded {sorted(recorded)}, now fires "
                          f"{sorted(got)}, lost {sorted(recorded - got)}")
    assert not broken, (
        "a signal edit left an existing judgment unsupported:\n  " + "\n  ".join(broken))
