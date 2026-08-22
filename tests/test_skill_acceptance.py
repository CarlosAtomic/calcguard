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
    """Does editing a signal change what fires on a judgment already pinned in code?

    Compared against a SNAPSHOT taken with the same scorer, not against the
    `signals:` the record's author wrote. Asking a different model to reproduce
    a Claude session's judgement tests whether two judges agree -- noise. The
    snapshot holds the judge fixed so the only variable is the signal wording.
    """
    r = _replay_module()
    if not r.ollama_up():
        pytest.skip("Ollama unreachable -- skipped, never a false green")
    baseline = r.load_baseline()
    if not baseline:
        pytest.skip("no baseline captured yet: replay.py --capture-baseline")
    model = os.environ.get("EJ_REGRESSION_MODEL", "deepseek-r1:32b")
    keys = {r.record_key(p) for p, _, _ in r.record_forks()}
    orphaned = set(baseline) - keys
    assert not orphaned, (
        f"baseline keys resolve to no record on disk: {sorted(orphaned)}.\n"
        "A record was renamed, renumbered or deleted. This MUST fail rather than\n"
        "skip -- a parallel session renumbered records on 2026-08-16, every key\n"
        "orphaned at once, and the guard silently protected nothing.")

    # The mirror of the orphan check, and the one that was missing. A record with
    # no baseline entry is skipped by the loop below, so it is UNPROTECTED while
    # the gate reports green. On 2026-08-22 the baseline held 7 keys against 12
    # records: five judgments -- JR-0008 through JR-0012 -- were covered by
    # nothing, and no output said so. An uncovered record must be as loud as an
    # orphaned key; both are the guard not guarding.
    uncovered = keys - set(baseline)
    assert not uncovered, (
        f"{len(uncovered)} of {len(keys)} records have NO baseline entry and are "
        f"therefore unprotected:\n  " + "\n  ".join(sorted(uncovered)) +
        "\n\nRe-capture deliberately: replay.py --capture-baseline --model <m>.\n"
        "NEVER re-capture to turn a red test green -- that moves the target.")

    moved = []
    for path, _recorded, body in r.record_forks():
        key = r.record_key(path)
        if key not in baseline:
            continue
        got, _runs = r.score_n(model, body)
        if got is None:
            pytest.skip(f"model call failed on {path.name} -- unscored, not passed")
        was = set(baseline[key])
        if got != was:
            moved.append(f"{key}: was {sorted(was)}, now {sorted(got)}")
    assert not moved, (
        "a signal edit moved what fires on an existing judgment:\n  "
        + "\n  ".join(moved)
        + "\n\nIf the change was intended, re-capture: "
          "replay.py --capture-baseline --model <m>")


# ---------------------------------------------------------------------------
# Record lint. A judgment record is a LEARNING ARTIFACT -- its value is the
# research it forced. These check for evidence of that loop, and above all that
# the decision is actually HELD: a pin naming a test that does not exist claims
# an enforcement it does not have, and nothing else notices.
#
# Deliberately unit-tested on synthetic records rather than scanning real ones.
# Scanning would turn calcguard's suite red for a malformed record in another
# repo, which calcguard cannot fix. Run the full scan explicitly:
#     python skills/engineering-judgment/acceptance/lint_records.py
# ---------------------------------------------------------------------------

LINT = Path(__file__).parent.parent / "src" / "calcguard" / "judgment_lint.py"

GOOD = """---
id: JR-0001
verdict: judged
signals: [2, 5]
pin: tests/test_thing.py::test_the_reading_is_pinned
---

## 1. The fork
Something the standard does not settle.

## 3. Candidate readings
Reading A gives one number and reading B gives another; A is the conservative
one because it minimises over a superset of the same terms.

## 4. Research
AISI S100-16 §J4.3.2, CS-0125 p. 141, and ESR-1271.

## 6. What would change this
A project that specifies its fastener, or a published value below the minimum.

## 7. Not covered
The branch selection has no oracle on the declared edition and is not settled
by this record.
"""


def _lint_module():
    spec = importlib.util.spec_from_file_location("lint_records", LINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MANIFEST = ("id,title,filename\n"
            "CS-0125,AISI S100-16 (2020) w/S2-20: North American Specification,s100-16.pdf\n"
            "CS-0528,Welded Box-Beam Flexure Design,tn-g104-14.pdf\n")


def _fake_repo(tmp_path, body, test_src="def test_the_reading_is_pinned():\n    pass\n",
               *, manifest=MANIFEST):
    (tmp_path / "docs" / "judgments").mkdir(parents=True)
    if manifest is not None:
        (tmp_path / "docs" / "judgments" / "cited-ids.csv").write_text(manifest)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_thing.py").write_text(test_src)
    p = tmp_path / "docs" / "judgments" / "JR-0001-a-slug.md"
    p.write_text(body)
    return p


def test_lint_passes_a_well_formed_record(tmp_path):
    assert _lint_module().lint(_fake_repo(tmp_path, GOOD)) == []


def test_lint_catches_a_DEAD_PIN(tmp_path):
    """The load-bearing check. Found this on a real record whose test was renamed."""
    p = _fake_repo(tmp_path, GOOD, test_src="def test_something_else():\n    pass\n")
    assert any("PIN IS DEAD" in v for v in _lint_module().lint(p))


def test_a_file_level_pin_is_legal_when_the_file_cites_the_record(tmp_path):
    """JR-0007 is enforced by seven tests and names the file, not one test.

    Requiring `file::test` flagged that as defective, which it is not. What must
    hold either way is that the link is real and traceable BOTH ways.
    """
    p = _fake_repo(tmp_path,
                   GOOD.replace("pin: tests/test_thing.py::test_the_reading_is_pinned",
                                "pin: tests/test_thing.py"),
                   test_src='"""Pins JR-0001."""\ndef test_a():\n    pass\n')
    assert _lint_module().lint(p) == []


def test_a_file_level_pin_is_caught_when_the_file_never_cites_the_record(tmp_path):
    """One-way link: the record claims the file, the file has never heard of it."""
    p = _fake_repo(tmp_path,
                   GOOD.replace("pin: tests/test_thing.py::test_the_reading_is_pinned",
                                "pin: tests/test_thing.py"),
                   test_src="def test_a():\n    pass\n")
    assert any("never cites" in v for v in _lint_module().lint(p))


def test_lint_catches_an_empty_not_covered(tmp_path):
    p = _fake_repo(tmp_path, GOOD[:GOOD.index("## 7. Not covered")] + "## 7. Not covered\n")
    assert any("Not covered" in v for v in _lint_module().lint(p))


def test_lint_catches_a_judged_record_with_no_candidate_readings(tmp_path):
    body = re.sub(r"## 3\. Candidate readings.*?(?=## 4\.)", "## 3. Candidate readings\n\n",
                  GOOD, flags=re.S)
    assert any("candidate readings" in v for v in _lint_module().lint(_fake_repo(tmp_path, body)))


def test_lint_catches_a_record_with_no_citation(tmp_path):
    body = GOOD.replace("AISI S100-16 §J4.3.2, CS-0125 p. 141, and ESR-1271.", "We looked at it.")
    assert any("no citation" in v for v in _lint_module().lint(_fake_repo(tmp_path, body)))


def test_lint_rejects_an_unknown_verdict(tmp_path):
    p = _fake_repo(tmp_path, GOOD.replace("verdict: judged", "verdict: probably_fine"))
    assert any("is not one of" in v for v in _lint_module().lint(p))


def test_a_draft_is_legal_and_needs_no_pin(tmp_path):
    """Research done, code has not moved. Legitimate -- but not settled."""
    body = GOOD.replace("verdict: judged", "verdict: draft").replace(
        "pin: tests/test_thing.py::test_the_reading_is_pinned", "pin: (none yet)")
    assert _lint_module().lint(_fake_repo(tmp_path, body)) == []


# ---------------------------------------------------------------------------
# Vault citation checks. A citation was only ever validated by SHAPE: the regex
# accepted `CS-0125` without ever asking whether CS-0125 exists or is the
# document the record claims. Two real records cited IDs that a Vault renumber
# had moved (CS-0726 -> CS-0730, CS-0728 -> CS-0731) and the lint called them
# clean, because a dead pointer and a live one are the same shape.
# ---------------------------------------------------------------------------


def test_a_cited_id_missing_from_the_manifest_is_caught(tmp_path):
    """A Vault renumber leaves the record pointing at nothing. This is the defect
    found on JR-0002 and JR-0005, which the shape check passed."""
    p = _fake_repo(tmp_path, GOOD.replace("CS-0125 p. 141", "CS-0726 p. 141"))
    assert any("CS-0726" in v for v in _lint_module().lint(p))


def test_a_document_that_is_not_what_the_record_claims_is_caught(tmp_path):
    """The fabricated-title failure: a real ID cited for a standard it is not."""
    p = _fake_repo(tmp_path, GOOD.replace("AISI S100-16 §J4.3.2, CS-0125 p. 141, and ESR-1271.",
                                          "ACI 318-19 §22.5, CS-0125 p. 141."))
    assert any("318-19" in v for v in _lint_module().lint(p))


def test_a_line_naming_several_standards_passes_when_one_matches(tmp_path):
    """GOOD's research line names S100-16 AND ESR-1271 beside CS-0125. Requiring
    every designation to match the title would fail a correct record."""
    assert _lint_module().lint(_fake_repo(tmp_path, GOOD)) == []


def test_a_record_citing_vault_ids_demands_a_manifest(tmp_path):
    """Absent manifest must be LOUD. A silent skip is a guard that never fires."""
    p = _fake_repo(tmp_path, GOOD, manifest=None)
    assert any("cited-ids.csv" in v for v in _lint_module().lint(p))


def test_a_record_citing_no_vault_ids_needs_no_manifest(tmp_path):
    """Not every record leans on the Vault; those must not be forced to carry one."""
    body = GOOD.replace("AISI S100-16 §J4.3.2, CS-0125 p. 141, and ESR-1271.",
                        "AISI S100-16 §J4.3.2, read from the printed standard.")
    assert _lint_module().lint(_fake_repo(tmp_path, body, manifest=None)) == []


def test_a_record_id_is_not_mistaken_for_a_vault_id(tmp_path):
    """JR-0001 matches the two-letter/four-digit shape and must not be looked up."""
    body = GOOD.replace("AISI S100-16 §J4.3.2, CS-0125 p. 141, and ESR-1271.",
                        "Supersedes JR-0004. AISI S100-16 §J4.3.2, CS-0125 p. 141.")
    assert _lint_module().lint(_fake_repo(tmp_path, body)) == []


def test_a_designation_carried_only_by_the_filename_still_matches(tmp_path):
    """CS-0528 and CS-0432 share the title "Welded Box-Beam Flexure Design"; only
    the filename says which edition. Matching on title alone failed JR-0008 and
    JR-0009 -- the two records that had been most careful about the edition."""
    body = GOOD.replace("AISI S100-16 §J4.3.2, CS-0125 p. 141, and ESR-1271.",
                        "CFSEI Tech Note G104-14, `CS-0528` p. 3.")
    assert _lint_module().lint(_fake_repo(tmp_path, body)) == []
