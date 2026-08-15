# Engineering Judgment Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Claude Code skill that resolves engineering forks — moments where a standard does not uniquely determine the answer — into cited, pinned, retrievable records.

**Architecture:** Markdown skill living in this repo, symlinked into `~/.claude/skills/`. Acceptance fixtures are authored first, from forks that actually occurred; the signal list is then written to catch them. A small pytest guards the two files against drift. calcguard's Python surface is untouched.

**Tech Stack:** Markdown, pytest (stdlib `re` only — no new dependencies), existing PATH tools `vault-search` / `vault-sections` / `llocal` / `kb-note`.

**Spec:** `docs/superpowers/specs/2026-08-15-engineering-judgment-design.md` (commit `603b4b1`). Cited by section below as *spec §N*.

**Branch:** `feat/engineering-judgment-skill` — already created, spec already committed. Do not merge to master; Carlos merges.

**Note on publicity:** this repo is public. The acceptance fixtures name AISI clauses and Carlos's own repos, the same disclosure the README already makes about the six motivating defects. No client data, no project drawings, no dimensions.

---

## File Structure

| Path | Responsibility |
|---|---|
| `skills/engineering-judgment/acceptance/forks.md` | the replay fixtures — 9 fork cases + 1 negative control |
| `skills/engineering-judgment/references/fork-signals.md` | the 9 signals, each with its check and receipt |
| `skills/engineering-judgment/SKILL.md` | frontmatter, trigger, sequence, verdicts |
| `skills/engineering-judgment/references/precedence.md` | ladder, conservatism rule, edition-delta protocol |
| `skills/engineering-judgment/references/research-protocol.md` | which command, in which order, what never to use |
| `skills/engineering-judgment/references/record-format.md` | record, pin, vault copy |
| `skills/engineering-judgment/references/parked-project-mode.md` | sealed-project material, parked |
| `skills/engineering-judgment/assets/judgment-record-template.md` | the output template |
| `tests/test_skill_acceptance.py` | structural drift guard between fixtures and signals |

---

## Task 1: Acceptance fixtures

Write these **before** the signal list. A signal invented first and justified afterward catches nothing.

**Files:**
- Create: `skills/engineering-judgment/acceptance/forks.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p skills/engineering-judgment/acceptance
```

- [ ] **Step 2: Write the fixture file**

The parser in Task 2 depends on this exact line format: `**Expected signals:** ` followed by comma-separated integers, or the literal word `none`. Keep it.

Create `skills/engineering-judgment/acceptance/forks.md`:

````markdown
# Acceptance fixtures — forks that actually happened

Each case states the situation with the **resolution withheld**. The skill passes a
case when scanning it trips at least the expected signals.

`tests/test_skill_acceptance.py` checks the structure of this file. It cannot check
the semantics — that is the replay in Task 10.

Format is load-bearing: `**Expected signals:**` takes comma-separated integers, or
`none`.

---

## FORK-1 — gusset joint adjacency

**Repo:** lgs-gusset
**Clause:** AISI S240-20 §E4.5.1
**Expected signals:** 3

**Context:** E4.5.1 sizes a gusset from the effective length across members meeting
at a panel point. The clause governs members that are "adjacent." At a joint where
members are ordered around the node, it is not stated whether the first and last
members — adjacent by wrapping the circle, separated by every other member if read
as a flat list — form an adjacent pair. The two readings give different `Leff` and
therefore a different capacity.

---

## FORK-2 — the effective length the engine cannot compute

**Repo:** lgs-truss-designer
**Clause:** AISI S240-20 §E4.5
**Expected signals:** 2

**Context:** The gusset provision requires `Leff`. Tracing its definition, the value
is set by the fabricated plate and fastener layout — information that lives on the
shop drawing. No input to the analysis engine supplies it, and no combination of the
engine's inputs derives it.

---

## FORK-3 — the bolt clause with no numbers in it

**Repo:** lgs-bolts
**Clause:** AISI S100-16 §J3.4
**Expected signals:** 1

**Context:** Implementing bolted connection shear. J3.4 is read in full. Its body
states the applicable requirement by pointing elsewhere; no nominal shear stress,
no resistance factor, and no material-specific value appears in the section text.

---

## FORK-4 — the clause that did not change and the figure that did

**Repo:** lgs-truss-designer
**Clause:** ASCE 7 §7.6.1
**Expected signals:** 4, 8

**Context:** Comparing two editions of ASCE 7 on file for the snow provision. The
prose of §7.6.1 reads identically between them. The section operates through a
referenced figure, which has not been opened in either edition. The declared basis
names one of the two editions.

---

## FORK-5 — the branch with nothing to check it against

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §J4.3.1
**Expected signals:** 6

**Context:** A screw-connection branch is implemented and returns a number. Searching
for something to check it against: no published worked example covers this
configuration, no licensed independent tool is available for it, and the expression
has no closed form or limiting case that constrains the result.

---

## FORK-6 — two elastic buckling clauses for one member

**Repo:** CFS_Box
**Clause:** AISI S100-16 §E2.2 / §E2.3
**Expected signals:** 3, 6

**Context:** Axial capacity needs elastic flexural-torsional buckling stress `Fcre`.
Two sections address it under conditions that overlap for the member in hand, and
the standard's scoping language does not clearly assign this member to one of them.
Neither branch has a worked example on file for this section shape.

---

## FORK-7 — two correct tables, combined

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §J3 with Appendix A
**Expected signals:** 7

**Context:** A bolted-connection capacity is assembled by taking a nominal shear
stress from one table and a geometric limit from another clause. Each value is read
correctly from its own source. Whether the standard permits that specific pairing —
whether the two tables share a scope — was not checked.

---

## FORK-8 — a method borrowed from the wrong material

**Repo:** lgs-gusset
**Clause:** AISI S240-20 §E4.5.1
**Expected signals:** 9

**Context:** A gusset compression check is available as the AISC Whitmore section
method, validated on hot-rolled plate. The plate here is cold-formed steel at a
thickness well below the range in which Whitmore was tested, and AISI supplies its
own plate-buckling provision for this case.

---

## FORK-9 — the clause that hands it back to you

**Repo:** lgs-truss-designer
**Clause:** *(to be filled from the repo's own history — see below)*
**Expected signals:** 5

**Context:** A provision states the quantity is permitted to be determined by
rational analysis, by test, or by accepted engineering principles, rather than
supplying an equation.

> **Sourcing note for the implementer:** signal 5 has no case on file yet. Find a
> real one by grepping the lgs docs for the standard's escape language before
> writing this case:
>
> ```bash
> rg -i "rational analysis|by test|accepted engineering" \
>    ~/projects/lgs-truss-designer/docs/ ~/projects/CFS_Box/docs/
> ```
>
> If it returns nothing, leave this case as written, and Task 3 records signal 5 in
> the test's `SIGNALS_WITHOUT_RECEIPT` set so the gap stays visible rather than
> silently absent.

---

## CONTROL-1 — negative control

**Repo:** lgs-truss-designer
**Clause:** AISI S100-16 §E3.2.1
**Expected signals:** none

**Context:** A flexural strength expression. The clause gives the equation inline
with every variable defined in the same section, the declared basis names exactly
one edition, no figure or appendix is referenced, a published worked example covers
this case, and no value from another table enters the calculation.

**This case must trip zero signals.** A signal list that fires here is a tax on every
clause, which is the friction this skill exists to avoid.
````

- [ ] **Step 3: Verify the format parses**

Run:
```bash
grep -c "^\*\*Expected signals:\*\*" skills/engineering-judgment/acceptance/forks.md
```
Expected output: `10`

- [ ] **Step 4: Commit**

```bash
git add skills/engineering-judgment/acceptance/forks.md
git commit -m "test: acceptance fixtures for the fork resolver

Nine forks that actually happened, plus a negative control. Written
before the signal list so the signals are derived from real failures
rather than invented and justified afterward.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 2: The drift guard (failing test)

**Files:**
- Create: `tests/test_skill_acceptance.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_skill_acceptance.py`:

```python
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
```

- [ ] **Step 2: Run it to verify it fails**

Run:
```bash
.venv/bin/python -m pytest tests/test_skill_acceptance.py -v
```

Expected: **2 passed, 2 failed.**

- PASS `test_every_case_declares_expected_signals` — reads only `forks.md`
- PASS `test_negative_control_trips_nothing` — reads only `forks.md`
- FAIL `test_every_expected_signal_is_defined` — `FileNotFoundError` on `fork-signals.md`
- FAIL `test_every_signal_has_a_fixture` — same

That split is correct and is the point of running it now: the fixture half is already
real, the signal half does not exist yet. If all four pass, the parser is silently
returning empty — check the heading and table regexes before continuing.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/test_skill_acceptance.py
git commit -m "test: drift guard between fixtures and signal list (failing)

Fails on the missing fork-signals.md, which Task 3 creates.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 3: The signal list

**Files:**
- Create: `skills/engineering-judgment/references/fork-signals.md`
- Modify: `tests/test_skill_acceptance.py` (only if signal 5 has no receipt)

- [ ] **Step 1: Create the directory**

```bash
mkdir -p skills/engineering-judgment/references skills/engineering-judgment/assets
```

- [ ] **Step 2: Write the signal list**

The table rows must start `| N |` with N the signal id — the Task 2 parser depends on
it. Content is spec §5.

Create `skills/engineering-judgment/references/fork-signals.md`:

````markdown
# Fork signals

Scan these before implementing any clause. **No hit means no fork: stop, and
implement normally.** The skill costs nothing on an unambiguous clause, and that is
deliberate.

Signals 1, 4, and 7 are mechanical — checkable without understanding the physics —
so they survive an implementer who is confidently wrong. Trust them most.

| # | Signal | How to check | Receipt |
|---|---|---|---|
| 1 | **Cross-reference body** | the clause text names another location instead of giving a value | J3.4 → Appendix A |
| 2 | **Undefined input** | the clause needs a quantity no input to the engine supplies | S240 §E4.5 `Leff` |
| 3 | **Ambiguous scope word** | "adjacent", "continuous", "supported", "effective" admits two readings that change the number | `joint_leff` |
| 4 | **Referenced artifact unread** | a figure, table, or appendix is cited and has not been opened | ASCE §7.6.1 figure |
| 5 | **Rational-analysis escape** | "permitted to be determined by rational analysis / by test" | the standard hands it to you |
| 6 | **No oracle** | no worked example, no independent tool, no closed form for this branch | §7.6.1, J4.3.1 |
| 7 | **Cross-table pairing** | two limits from different clauses are combined; is the pair legal? | the 1.43× unconservative pair |
| 8 | **Edition delta on the path** | the declared edition and another on file differ *at this clause* | S2-20 vs S3-22 |
| 9 | **Outside tested range** | a listing or equation is applied beyond its validated span, thickness, or spacing | scope is a gate, not a preference |

## Notes on the ones that mislead

**Signal 4 is about what you have opened, not what you have read about.** A figure
summarised in a preface is not a figure you have read. ASCE §7.6.1's prose was
identical across two editions while its figure gained a √Is term and a cap.

**Signal 7 fires on correct inputs.** Both values can be read perfectly from their own
tables and still not be combinable. Mutation testing cannot find this, because every
mutation is on the wrong axis — it perturbs the values, not the pairing.

**Signal 8 produces a diff, never a verdict.** Record where the editions agree and
where they do not. A newer edition does not invalidate the declared one, and is
frequently narrower. See `precedence.md`.

**Signal 9 cuts both ways.** Outside the tested range a listing is *silent*, not
permissive. Drop back to the general provision rather than extrapolating.
````

- [ ] **Step 3: Run the test**

Run:
```bash
.venv/bin/python -m pytest tests/test_skill_acceptance.py -v
```

Expected: all four PASS — **unless** FORK-9 was left unsourced in Task 1, in which
case `test_every_signal_has_a_fixture` FAILS naming signal 5.

- [ ] **Step 4: If and only if that test failed, record the gap**

Edit `tests/test_skill_acceptance.py`, changing the one line:

```python
SIGNALS_WITHOUT_RECEIPT: set[int] = {5}  # rational-analysis escape: no case on file yet
```

Re-run; expected: 4 passed.

- [ ] **Step 5: Run the whole suite**

Run:
```bash
.venv/bin/python -m pytest tests/ -q
```
Expected: `43 passed` (39 existing + 4 new).

- [ ] **Step 6: Commit**

```bash
git add skills/engineering-judgment/references/fork-signals.md tests/test_skill_acceptance.py
git commit -m "feat: the nine fork signals

Derived from the acceptance fixtures, not the reverse. Drift guard green.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 4: SKILL.md

**Files:**
- Create: `skills/engineering-judgment/SKILL.md`

- [ ] **Step 1: Write it**

The `description` field decides whether the skill ever loads. It must trigger on the
*implementer's* situation, not on a user phrase, because the user is not the one who
notices a fork.

Create `skills/engineering-judgment/SKILL.md`:

````markdown
---
name: engineering-judgment
description: >-
  Use when implementing or reviewing a code clause in an engineering calculation program
  and the standard may not uniquely determine the answer — the clause body is a
  cross-reference, it needs a value no input supplies, a scope word like "adjacent" or
  "continuous" admits two readings, a referenced figure or appendix has not been opened,
  it says "by rational analysis", the branch has no worked example or independent tool,
  two tables from different clauses are being combined, editions on file differ at this
  clause, or a method is applied outside its tested range. Also use for "which reading
  governs", "what does this clause actually require", "the older edition said this",
  "is this pairing legal", "what's our basis for this", and before choosing between two
  defensible interpretations. Produces a cited judgment record, never an edited calc.
---

# Engineering Judgment

calcguard asserts physics — equilibrium, sign, scaling, closed form. It answers *does
this satisfy the equation it was pointed at?*

This skill answers what comes earlier: **which clause, which edition, which reading?**
The standard does not always determine that, and where it does not, someone chooses.
This makes the choice cited, recorded, and pinned instead of silent.

The two never exchange data. calcguard stays exactly as it is.

## Non-negotiable

- **Never edit the calculation.** Issue a record. The engineer decides.
- **Retrieval, never recall.** Every value driving a resolution cites a document on
  file with edition and section. No remembered φ, no remembered table.
- **Return *Insufficient basis* freely.** A resolver that always reaches a verdict is
  a rubber stamp. Naming the missing document is a useful answer.
- **Carlos decides.** Records carry `decided_by`, and it is not this skill.

## Sequence

### 0. Read the basis

Read `code-basis.toml` from the project root. It declares the governing standards and
is a project decision, never inferred from publication dates.

Absent? Ask which code the project is on, and do not advise until answered. Do **not**
interrogate for jurisdiction, permit date, or risk category — a calc engine has none.

### 1. Scan the signals

Work `references/fork-signals.md`. **No hit → stop, implement normally.** Say nothing.

### 2. State the fork in one line

Before any research. Research conducted after a reading is chosen will find support
for that reading.

### 3. Write the independent expectation

Before reading sources: what do you expect, and why? A golden number read first moves
the target instead of failing.

### 4. Research

Per `references/research-protocol.md`. Declared edition first.

### 5. Resolve

Per `references/precedence.md` — ladder, then the conservatism rule.

### 6. Emit

Per `references/record-format.md` — record, vault copy, pin.

## Verdicts

| Verdict | Meaning | Must state |
|---|---|---|
| **Determined** | the standard resolves it | edition + section |
| **Judged** | it does not; a reading was chosen | candidate readings, which is conservative, what would change the choice, who decides |
| **Insufficient basis** | the library lacks it | the document to acquire |
| **Alternative means** | less conservative than the declared basis permits | named as IBC §104.11, not applied silently |

*Alternative means* is top-level so it cannot hide inside a *Judged*. Never soften a
*Judged* into a *Determined*: a citation that does not settle the question is
research, not authority.

## Files

- `references/fork-signals.md` — the nine signals
- `references/precedence.md` — ladder, conservatism rule, edition deltas
- `references/research-protocol.md` — which command, in which order
- `references/record-format.md` — record, pin, vault copy
- `references/parked-project-mode.md` — sealed-project review; **out of scope here**
- `assets/judgment-record-template.md` — the template
- `acceptance/forks.md` — the fixtures this skill is tested against

## Boundaries

For the design provisions themselves, defer to `cfs-structural-design`,
`concrete-design`, `wood-design`, `hot-rolled-steel-design`, `cfs-fire-code-authority`,
`engineer-skill`. For document discovery and the basis gate, `reference-library`.

This skill adjudicates a fork. It does not supply the provision and does not review a
sealed design.
````

- [ ] **Step 2: Verify the frontmatter parses**

Run:
```bash
head -3 skills/engineering-judgment/SKILL.md
```
Expected: line 1 is `---`, line 2 begins `name: engineering-judgment`.

- [ ] **Step 3: Commit**

```bash
git add skills/engineering-judgment/SKILL.md
git commit -m "feat: engineering-judgment SKILL.md

Trigger fires on the implementer's situation, not a user phrase -- the
user is not the one who notices a fork.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 5: precedence.md

**Files:**
- Create: `skills/engineering-judgment/references/precedence.md`

- [ ] **Step 1: Write it**

Content is spec §6.1 and §6.2. The conservatism rule is quoted verbatim below because
its asymmetry is the whole point and paraphrase erodes it.

Create `skills/engineering-judgment/references/precedence.md`:

````markdown
# Precedence and conflict resolution

Sources will disagree. Resolve the same way every time, or this becomes a coin flip
with citations attached.

## The ladder

Higher rungs govern lower for the question at issue.

1. Adopted building code and its amendments, at the declared edition
2. Reference standards as adopted by that edition, including adopted supplements
3. Product evaluation reports and listed assemblies, **where the configuration matches**
4. Manufacturer test data, where independently traceable
5. Newer editions, research literature, industry technical notes — admissible as judgment, not adopted
6. Textbook method and first principles

**Specific beats general, inside the tested limits only.** Outside them a listing is
silent, not permissive, and the general provision returns. Check span, thickness,
spacing, fastener, and substrate against the listing before crediting it.

## The conservatism rule

> A non-adopted source that makes the design **more conservative** than the declared
> basis may be applied freely, cited as judgment.
>
> A non-adopted source that makes the design **less conservative** may not be applied
> on its own authority. Name it as an IBC §104.11 alternative means.

The asymmetry is the rule. You are always free to be stricter. You are never free to
be more permissive without the door the code provides.

Say it plainly when it comes up: *"The newer edition permits X; the declared basis
does not. Applying X requires a §104.11 submission. Under the declared basis the
resolution is [verdict]."* Do not use the relaxed provision quietly, and do not
pretend the newer document is absent.

## When the newer source reveals a problem

The inverse case hides easily. Sometimes a newer edition, an errata, or a paper shows
the **declared** provision is unconservative for this condition — a limit state later
found to govern, a knock-down factor added, an equation corrected.

Code compliance is the floor, not the ceiling. Say so, cite the newer source, state
the exposure. This is the one place where *"it passed the code check"* is the wrong
answer.

Check for errata to the declared edition during retrieval. Errata apply to the
declared edition and are routinely missed.

## Edition deltas — signal 8

A delta is **evidence, not a verdict.** Produce a clause-by-clause comparison: where
the editions give the same number, and where they do not.

Three rules:

- **A newer edition does not invalidate the declared one.** It is frequently
  *narrower*, not better.
- **The basis is a project decision** fixed in `code-basis.toml`, never re-derived
  from publication dates, publishers, or supplement numbers. This engine was migrated
  off its adopted edition twice by reasoning from newest-published.
- **Where a newer edition supplies logic the engine lacks, take the logic and apply it
  with the declared edition's own formulas and factors.** Cite the number to the
  edition it came from.

The worked model is `lgs-truss-designer/docs/EDITION-DELTA-S2-20-vs-S3-22.md`.

## Precedent from past work

Prior projects are a consistency check, never authority.

- Useful: *"Three comparable spans landed in this capacity band; this sits well outside it."*
- Not useful: *"We did it this way last time."* Precedent inherits its errors.

When precedent conflicts with the declared basis, the basis wins and the precedent
becomes its own finding — it may indicate a systematic issue across past work.
````

- [ ] **Step 2: Commit**

```bash
git add skills/engineering-judgment/references/precedence.md
git commit -m "feat: precedence ladder and the conservatism rule

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 6: research-protocol.md

**Files:**
- Create: `skills/engineering-judgment/references/research-protocol.md`

- [ ] **Step 1: Write it**

Content is spec §4 step 4 plus §8.3's three retrieval facts.

Create `skills/engineering-judgment/references/research-protocol.md`:

````markdown
# Research protocol

## Never grep the vault PDFs

```bash
rg -i "web crippling" ~/Vault          # WRONG
```

The vault holds 4,269 PDFs. Text search across them returns a clean, confident zero
that says nothing about the corpus — a false negative that looks exactly like a true
one. Use the tools that index extracted text.

## Order

Specific to general. Stop when the authority is found and confirmed.

**1. The provision.** Resolves a query to a section across ~92k cataloged headings.

```bash
~/bin/vault-sections "gusset plate" --topic CS --json
```

**2. The document,** with the basis gate. Always `--json`; it returns `code_family`,
`edition_year`, `supplement`, and `is_declared_basis`, and announces the applied basis
and its path on stderr.

```bash
~/bin/vault-search "distortional buckling" --material CFS --json
```

**3. The contents.** Merged RAG answer plus on-file catalog citations.

```bash
llocal research "AISI S240 gusset effective length"
```

**4. Prior judgments.** `JR-` records live in the `notes` workspace, **not** the
catalog. `vault-search` will not find them.

```bash
llocal rag notes "gusset Leff adjacency"
```

**5. Every edition on file,** with publisher and adopting-code reference status. It
ranks nothing, on purpose.

```bash
codes-table
```

## The basis gate

Apply `reference-library`'s rules — they are not restated here, to keep one source of
truth:

- `basis: none declared` → ask; do not advise
- the declared hit is marked `<- DECLARED BASIS` → cite it
- a hit that is not declared is still a real document → do not call it obsolete or
  superseded; offer it as research
- `!! basis declares X - NOT ON FILE` → say so; never cite the nearest thing
- `NO REFERENCE FOUND` → say so; never invent a citation

## Reading a clause

**Open what it references.** A clause body is not the clause when it points to an
appendix, a figure, or a table. Signal 1 and signal 4 exist because both have already
cost real numbers.

**Read the whole scope statement,** not the equation. A pairing is legal or not
because of scope, and scope lives in the prose above the equation.

**When comparing editions, diff what the clause references,** not only its text. Prose
identical between editions is not the same provision if its figure changed.

## Gaps

When the library lacks it, produce a gap entry, not a guess:

```markdown
### Gap — <what is missing>
- Needed for: <which fork>
- Searched: <commands and terms tried>
- Effect: held at Insufficient basis
- To resolve: <the specific document to acquire>
```

Gaps accumulate into the acquisition list. They are telling you which documents the
work actually needs.
````

- [ ] **Step 2: Verify every referenced tool exists**

Run:
```bash
for t in vault-sections vault-search llocal codes-table; do
  test -x ~/bin/$t && echo "OK   $t" || echo "MISS $t"; done
```
Expected: four `OK` lines. A `MISS` means the protocol cites a tool that is not
installed — fix the protocol or install the tool before continuing.

- [ ] **Step 3: Commit**

```bash
git add skills/engineering-judgment/references/research-protocol.md
git commit -m "feat: research protocol -- catalog and RAG, never grep over PDFs

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 7: record-format.md and the template

**Files:**
- Create: `skills/engineering-judgment/references/record-format.md`
- Create: `skills/engineering-judgment/assets/judgment-record-template.md`

- [ ] **Step 1: Write the format reference**

Content is spec §8.

Create `skills/engineering-judgment/references/record-format.md`:

````markdown
# The record, the pin, the vault copy

## Where

`docs/judgments/JR-NNNN-<slug>.md` in the **consuming repo** — the repo whose code the
decision governs, not this one. It travels with the code and shows in the diff.

Next id: the highest `JR-` in that repo's `docs/judgments/`, plus one. Start at
`JR-0001`.

## Frontmatter

```yaml
---
id: JR-0001
clause: AISI S240-20 §E4.5.1
basis: AISI S100-16 (2020) w/S2-20   # full declared designation, supplement included
repo: lgs-truss-designer
commit: <sha at resolution>
signals: [2, 3]
verdict: judged                       # determined | judged | insufficient_basis | alternative_means
decided_by: Carlos
date: 2026-08-15
pin: tests/test_gusset_layout.py::test_wrap_around_pair_is_adjacent
---
```

`basis` carries the supplement. A clause number without one is unresolvable.

## Body

Seven sections, in order. `assets/judgment-record-template.md` is the fill-in copy.

1. **The fork** — one line
2. **Independent expectation** — what was expected, recorded before research
3. **Candidate readings** — each with its consequence for the number
4. **Research** — citations with edition, section, locator
5. **Resolution** — the reading chosen, the ladder rung that governed, why
6. **What would change this** — the condition that reopens the fork
7. **Not covered** — mandatory

**Section 7 is what keeps the record honest.** It is easy to write "resolved" and
stop. Name what this record does not settle.

## The pin

Every `judged` and every `alternative_means` record names a test in the consuming
repo that asserts the chosen reading. Its docstring cites the record id.

```python
def test_wrap_around_pair_is_adjacent():
    """Pins JR-0001: E4.5.1 "adjacent" includes the wrap-around pair.

    Reversing this reading is a design decision, not a refactor. If this
    fails, read docs/judgments/JR-0001-*.md before changing it.
    """
    joint = Joint(members=[m0, m1, m2, m3])
    assert (m0, m3) in adjacent_pairs(joint)
```

Prose explains; the assertion enforces. A `determined` record needs no pin — the
standard already settles it.

## The vault copy

```bash
/home/atomicjr/projects/spark-powerhouse/ingest/.venv/bin/kb-note decision \
  "JR-0001 AISI S240-20 E4.5.1 gusset adjacency" \
  --project lgs-truss-designer \
  --source JR-0001 \
  --tags "judgment,AISI,S240,gusset" \
  --body "<the resolution and what would change it>"
```

Then:

```
Inbox/ --03:15 notes-sync.sh--> Decisions/ --kb-ingest--> `notes` workspace
```

Three facts, not assumptions:

- **`decision` is the type.** An unrecognised type falls back to `Findings`
  (`consolidate.py:64`).
- **Discovery is `llocal rag notes`, not `vault-search`.** The catalog indexes PDFs.
- **Repo-visible immediately, vault-discoverable after 03:15.** For same-day
  cross-project lookup, run the sync manually:

  ```bash
  /home/atomicjr/projects/spark-powerhouse/ingest/.venv/bin/kb-ingest --source notes --verbose
  ```

`Decisions/` may not exist yet. Verify it after the first promotion rather than
assuming it appeared.

## Consult before deriving

Before resolving any fork, check whether it is already resolved:

```bash
llocal rag notes "<clause> <the ambiguous term>"
ls ~/projects/*/docs/judgments/ 2>/dev/null
```

A fork resolved once should never be re-litigated.
````

- [ ] **Step 2: Write the template**

Create `skills/engineering-judgment/assets/judgment-record-template.md`:

````markdown
---
id: JR-NNNN
clause:
basis:
repo:
commit:
signals: []
verdict:
decided_by: Carlos
date: YYYY-MM-DD
pin:
---

# JR-NNNN — <clause>, <the question in five words>

**Verdict:** <determined | judged | insufficient basis | alternative means>

## 1. The fork

<One line: what is undetermined, and what turns on it.>

## 2. Independent expectation

*Recorded before research.*

- Expected answer or band:
- Expected governing limit state:
- Basis for the expectation:

## 3. Candidate readings

| Reading | Consequence for the number | More or less conservative |
|---|---|---|
| A | | |
| B | | |

## 4. Research

| Source | Edition | Section | Locator | Ladder rung |
|---|---|---|---|---|

<Signal 8: put the clause-by-clause edition delta here. Evidence, not a verdict.>

## 5. Resolution

**Reading chosen:** <A or B>
**Governing ladder rung:** <1-6>
**Why:**

<If less conservative than the declared basis: name it IBC §104.11 alternative means,
and state that it is NOT applied on this skill's authority.>

## 6. What would change this

<The specific condition that reopens the fork.>

## 7. Not covered

*Mandatory.* <What this record does NOT settle.>

---

*Advisory. The engineer of record retains sole responsibility for the design and its
seal.*
````

- [ ] **Step 3: Commit**

```bash
git add skills/engineering-judgment/references/record-format.md \
        skills/engineering-judgment/assets/judgment-record-template.md
git commit -m "feat: record format, pin, and vault ingest path

Format generalized from lgs EDITION-DELTA-S2-20-vs-S3-22.md. Ingest path
verified live: notes-sync 2026-08-14, indexed=1 failed=0.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 8: Park the sealed-project material

Salvage from the Claude Desktop draft so the writing is not lost. **Do not wire it
into the sequence.**

**Files:**
- Create: `skills/engineering-judgment/references/parked-project-mode.md`

- [ ] **Step 1: Write it**

Source material is at
`/tmp/claude-1000/-home-atomicjr/16f964e3-4742-4058-99db-cd0b7ac3aa9a/scratchpad/ej/`
(`design-basis.md`, `silent-failures.md`). If that scratchpad is gone, re-extract:

```bash
mkdir -p /tmp/ej && cd /tmp/ej && unzip -o /mnt/nas/Projects/Claude/files2.zip
```

Create the file with the header below, then append exactly these two extracts, in
this order, under a `## Salvaged: design basis` and a `## Salvaged: review checklist`
heading:

```bash
EJ=/tmp/claude-1000/-home-atomicjr/16f964e3-4742-4058-99db-cd0b7ac3aa9a/scratchpad/ej
sed -n '32,83p' "$EJ/design-basis.md"      # §2 why current code is not the truth
                                            #  → §5 existing structures
sed -n '39,94p' "$EJ/silent-failures.md"   # §3 load path → §8 material traps
```

Line ranges verified against the headings on 2026-08-15. If the scratchpad was
re-extracted and they moved, re-derive with `grep -n "^## "` rather than trusting
these numbers.

Take the text verbatim. Do not edit it to fit the fork resolver — it is parked
precisely so it stays intact for its own job.

````markdown
# Parked: sealed-project review

**Not part of this skill's sequence. Do not run any of it during clause
implementation.**

This is review material for *sealed project work* — judging whether a specific
building's calculation is correct and sealable. That is a different job from
resolving a fork in a calc engine, and mixing them produced a skill that halted on
jurisdiction and permit date while implementing a Python function.

Kept because the material is correct for its own job and worth not rewriting. It
becomes a separate skill if and when that work needs one.

**What is parked here:** permit-date governance and the concurrency question; state
and local amendments; the Chapter 35 adoption chain; IEBC triggers and existing
structures; load path continuity to the foundation; serviceability against the actual
finish rather than a default L/240; order-of-magnitude and precedent checks;
constructability, erection stability, and shipping and lifting cases for panelized
work; and the material-specific trap lists for CFS, concrete, wood, and hot-rolled
steel.

**Why none of it belongs in the fork resolver:** a calc engine has no permit date, no
jurisdiction, no drawings to check an unbraced length against, and no site. Demanding
them blocks every invocation.

---

<salvaged content follows>
````

- [ ] **Step 2: Verify it is genuinely inert**

Run:
```bash
grep -rn "parked-project-mode" skills/engineering-judgment/SKILL.md
```
Expected: exactly one hit, in the Files list, labelled **out of scope here**. If the
sequence references it, remove that reference.

- [ ] **Step 3: Commit**

```bash
git add skills/engineering-judgment/references/parked-project-mode.md
git commit -m "docs: park the sealed-project review material

Correct for its own job, wrong for clause implementation. Kept intact,
wired into nothing.

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 9: Install by symlink

**Files:**
- Create: symlink `~/.claude/skills/engineering-judgment`

- [ ] **Step 1: Confirm nothing is there**

```bash
ls -la ~/.claude/skills/engineering-judgment 2>&1
```
Expected: `No such file or directory`. If a **real directory** exists, stop and ask
Carlos — do not delete it.

- [ ] **Step 2: Link**

```bash
ln -s /home/atomicjr/projects/calcguard/skills/engineering-judgment \
      /home/atomicjr/.claude/skills/engineering-judgment
```

- [ ] **Step 3: Verify the installed copy is the repo file, not a copy**

```bash
readlink ~/.claude/skills/engineering-judgment
diff <(cat ~/.claude/skills/engineering-judgment/SKILL.md) \
     <(cat skills/engineering-judgment/SKILL.md) && echo "IDENTICAL"
```
Expected: the readlink prints the calcguard path, then `IDENTICAL`.

`reference-library` was installed as a copy and silently diverged. This is why.

- [ ] **Step 4: Full suite**

```bash
.venv/bin/python -m pytest tests/ -q
```
Expected: `43 passed`.

---

## Task 10: Acceptance replay

The semantic test. The pytest in Task 2 only guards structure.

- [ ] **Step 1: Run the replay**

For **each** of the 10 cases in `acceptance/forks.md`, dispatch a **fresh** subagent —
fresh so it cannot see the expected answer — with this prompt, substituting the case's
Context verbatim:

```
Below are nine signals that indicate an engineering standard may not
uniquely determine an answer.

<paste the signal table's `#`, `Signal` and `How to check` columns ONLY --
 see the withholding rule below -- plus the "Notes on the ones that
 mislead" section>

Scan this clause-implementation situation against those nine signals.
List ONLY the signal numbers that fire, as a JSON array. If none fire,
return []. Do not explain.

Situation:
<paste the case's **Context** block verbatim — nothing else>
```

**Withholding rule — the replay is invalid without it.** Do NOT tell the agent to
read `fork-signals.md`, and do NOT include the **Receipt** column. Each receipt names
the very clause its fixture describes — signal 1's receipt is `J3.4 → Appendix A` and
FORK-3's Context names J3.4; signal 9's is `Whitmore on CFS plate` and FORK-8's Context
names Whitmore. Handed the full table, an agent scores by matching clause strings
rather than by reading the situation, and the suite passes for the wrong reason.

The receipts stay in the file — they are why each signal exists — but they are
documentation for the implementer, not part of the detection procedure.

Also withhold: the case id, how many cases exist, and that a negative control is among
them. Dispatch the cases in a shuffled order.

- [ ] **Step 2: Score**

| Case | Passes when |
|---|---|
| FORK-1 … FORK-9 | the returned array contains **at least** the case's expected signals |
| CONTROL-1 | the returned array is **exactly** `[]` |

- [ ] **Step 3: Act on failures**

- **A FORK case missed its signal** → the signal's *How to check* is too vague. Sharpen
  it in `fork-signals.md`, re-run that case. Do not change the fixture.
- **CONTROL-1 fired** → a signal is over-broad. Narrow it. This failure matters more
  than a miss: an over-firing list becomes a tax on every clause and gets bypassed.

- [ ] **Step 4: Record the result**

Append to `skills/engineering-judgment/acceptance/forks.md`:

```markdown
---

## Replay log

| Date | Cases passed | Control clean | Notes |
|---|---|---|---|
| 2026-08-15 | N/9 | yes/no | |
```

- [ ] **Step 5: Commit**

```bash
git add skills/engineering-judgment/
git commit -m "test: acceptance replay -- N/9 forks flagged, control clean

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 11: First live run

Prove it end to end on a real open fork. Per spec §11: **§7.6.1 or J4.3.1 in lgs**,
both un-oracled today.

**This task runs in the lgs repo, not calcguard.** Use a worktree — never branch or
commit in a shared checkout.

- [ ] **Step 1: Worktree**

```bash
cd ~/projects/lgs-truss-designer
git worktree add ~/lgs-jr-0001 -b feat/jr-0001-first-judgment
cd ~/lgs-jr-0001
```

- [ ] **Step 2: Run the skill on the fork**

Invoke `engineering-judgment` on AISI S100-16 §J4.3.1 as implemented in lgs. Follow
the sequence: read `code-basis.toml`, scan signals, state the fork, write the
expectation, research, resolve, emit.

- [ ] **Step 3: Verify the record**

```bash
ls docs/judgments/
head -15 docs/judgments/JR-0001-*.md
```
Expected: the file exists, frontmatter carries `decided_by: Carlos`, and `basis`
matches `code-basis.toml`'s designation **including its supplement**.

- [ ] **Step 4: Verify the pin actually fails**

A pin that cannot fail is worse than no pin. Invert the pinned reading in the source,
run the pinned test, confirm FAIL, then restore.

```bash
# edit the source to reverse the chosen reading, then:
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python -m pytest <the pin path> -v
```
Expected: **FAIL**, with the record id visible in the docstring. Then `git checkout --`
the source and confirm it passes.

Thread pins are mandatory: unpinned, this suite runs ~7 hours instead of ~90s.

- [ ] **Step 5: Vault copy and same-day retrieval**

```bash
/home/atomicjr/projects/spark-powerhouse/ingest/.venv/bin/kb-note decision \
  "JR-0001 <title>" --project lgs-truss-designer --source JR-0001 \
  --tags "judgment,AISI,S100" --body "<resolution>"

ls /mnt/nas/Projects/Documents/_vault/Inbox/

/home/atomicjr/projects/spark-powerhouse/ingest/.venv/bin/kb-ingest --source notes --verbose

llocal rag notes "J4.3.1 screw connection"
```
Expected: the note appears in `Inbox/`, ingest reports `indexed=1 failed=0`, and the
rag query returns the record.

- [ ] **Step 6: Verify `Decisions/` on first promotion**

After the next 03:15 sync — or by running `kb-consolidate` directly:

```bash
/home/atomicjr/projects/spark-powerhouse/ingest/.venv/bin/kb-consolidate
ls /mnt/nas/Projects/Documents/_vault/Decisions/
```
Expected: `Decisions/` exists and holds the note. It did not exist before this run;
confirm rather than assume.

- [ ] **Step 7: Commit, do not merge**

```bash
git add docs/judgments/ <the pin test path>
git commit -m "feat: JR-0001 -- first judgment record, with pin

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

Leave both branches unmerged. Carlos merges.

---

## Done when

1. `.venv/bin/python -m pytest tests/ -q` → **43 passed**
2. `readlink ~/.claude/skills/engineering-judgment` → the calcguard path
3. Replay: 9/9 forks flagged, CONTROL-1 returns `[]`
4. `JR-0001` committed in lgs, its pin **verified to fail** when reversed
5. `llocal rag notes` returns the record
6. Both branches unmerged
