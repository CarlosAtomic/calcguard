---
name: engineering-judgment
description: >-
  Use when implementing or reviewing a code clause in an engineering calculation program
  and the standard may not uniquely determine the answer — the clause body is a
  cross-reference, it needs a value no input supplies, a scope word like "adjacent" or
  "continuous" admits two readings, or two clauses' applicability overlaps for the member
  in hand, a referenced figure or appendix has not been opened, the clause defers
  determination to rational analysis, to test, or to engineering judgment, or otherwise
  states who decides rather than what the answer is, the branch has no worked example or
  independent tool, two tables from different clauses are being combined, more than one
  edition on file bears on this clause whether or not a difference is yet known, or a
  method is applied outside its tested range. Also use for "which reading governs", "what
  does this clause actually require", "the older edition said this", "is this pairing
  legal", "what's our basis for this", and before choosing between two defensible
  interpretations. Produces a cited judgment record, never an edited calc.
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
