# engineering-judgment — design

**Status:** spec, 2026-08-15
**Ships as:** a Claude Code skill in this repo, symlinked into `~/.claude/skills/`
**Relationship to calcguard:** sibling, not successor. calcguard stays exactly as it is.

---

## 1. Why

calcguard asserts physics: equilibrium, sign, scaling, closed form, coverage. It
answers *"does this satisfy the equation it was pointed at?"* It caught six defects
that a 1277-test suite missed, and it remains the right tool for that job.

It cannot answer a different question that arises earlier: **which clause, which
edition, and which reading?** That question has no assertion, because the standard
itself does not always determine the answer.

Every one of these is open or half-buried today:

| Fork | Where it stands |
|---|---|
| `joint_leff` wrap-around adjacency | resolved as a "conservative interpretation" of AISI E4.5.1; the reasoning lives in a memory note, attached to no code |
| AISI S240-20 §E4.5 `Leff` | the standard needs a value fixed by the shop drawing, which the engine cannot compute |
| AISI S100 J3.4 | the clause body is a pure cross-reference; every bolt value lives in Appendix A |
| ASCE 7 §7.6.1 | prose identical between editions, but the referenced **figure** gained √Is and a cap |
| §7.6.1, J4.3.1 | un-oracled in lgs right now |
| §E2.2 / §E2.3 axial Fcre | parked in the CFS_Box research plan |

Each was decided, or deferred, by reasoning that no later reader can find. A
decision nobody can find gets made again, differently.

**This skill makes that decision retrievable, cited, and pinned.**

## 2. What it is

A fork resolver. It fires at one moment: when the standard does not uniquely
determine the answer and the implementer would otherwise choose a reading silently.

Three properties follow, and they are the design:

- **Demand-driven.** No fork, no invocation, no cost. It is not a gate and does not
  run on a schedule.
- **Retrieval, never recall.** Every value that drives a resolution cites a document
  on file, with edition and section. Absent that, the verdict is *Insufficient basis*.
- **It never edits the calculation.** It issues a record. The engineer decides.

## 3. What it is not

- Not a replacement for calcguard. The two never exchange data. Delete the
  `calcguard-input.schema.json` coupling invented in the Claude Desktop draft;
  calcguard is deliberately not domain-aware and must not learn `permit_date`.
- Not a code-compliance reviewer for sealed project work. That material is real and
  is **parked**, not discarded (§10).
- Not a second source of truth for which edition governs. `code-basis.toml` owns
  that, and this skill reads it.
- Not a supersession engine. The `_GOVERNING` / `is_pinned` / `code_status` model was
  deleted from `vault-catalog` on 2026-08-10 after it shipped the wrong edition twice.
  It does not come back here under a new name.

## 4. Success criteria

1. On a clause with no ambiguity, the skill fires **zero** times and adds no steps.
2. Each of the six forks in §1, replayed, trips at least one enumerated signal.
3. A resolution written today is retrievable by a different project tomorrow.
4. Reversing a resolution in code **fails a test** that names the record.
5. Returning *Insufficient basis* is a normal outcome, not a failure of the run.

Criterion 2 is the acceptance test. Applying calcguard's own standard — *a
verification tool that cannot catch known bugs is decorative* — a fork resolver that
cannot flag the forks already paid for is decorative too.

## 5. Fork signals

The trigger is an enumerated list, scanned before implementing any clause. Signals
1, 4, and 7 are mechanical: they can be checked without understanding the physics,
so they survive an implementer who is confidently wrong.

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

Signal 8 produces a **diff presented as evidence**. It never produces a verdict that
one edition supersedes another.

## 6. Sequence

| # | Step | Rule |
|---|---|---|
| 0 | Read the basis | Read `code-basis.toml`. Ask only when it is absent. No multi-element interrogation. |
| 1 | Scan the signals | No hit → exit silently. |
| 2 | State the fork in one line | Written **before** research, so research cannot rationalize a reading already chosen. |
| 3 | Write the independent expectation | Written **before** reading sources. A bad golden number moves the target instead of failing. |
| 4 | Research | `vault-sections` → `vault-search --json` → `llocal research` → the `reference-library` gate. |
| 5 | Resolve | Precedence ladder, then the conservatism rule. |
| 6 | Emit | Record, vault copy, pin. |

**Step 4 forbids `rg` and `grep` over the vault PDFs.** Text search across 4,269 PDFs
returns a confident, clean zero that means nothing about the corpus. Use the catalog
and the RAG, which index extracted text.

### 6.1 Precedence ladder

Higher rungs govern lower ones for the question at issue.

1. Adopted building code and its amendments, at the declared edition
2. Reference standards as adopted by that edition, including adopted supplements
3. Product evaluation reports and listed assemblies, **where the configuration matches**
4. Manufacturer test data, where independently traceable
5. Newer editions, research literature, industry technical notes — admissible as judgment, not adopted
6. Textbook method and first principles

Specific beats general, but only inside the tested limits. Outside them a listing is
silent, not permissive, and the general provision returns.

### 6.2 The conservatism rule

> A non-adopted source that makes the design **more conservative** than the declared
> basis may be applied freely, cited as judgment.
>
> A non-adopted source that makes the design **less conservative** may not be applied
> on its own authority. Name it as an IBC §104.11 alternative means.

The asymmetry is the rule. You are always free to be stricter. You are never free to
be more permissive without the door the code provides.

The inverse case matters and hides easily: when a newer source shows the **adopted**
provision is unconservative for this condition, code compliance is the floor, not the
ceiling. Say so.

## 7. Verdicts

Decision vocabulary, not grading vocabulary. A reviewer grades a finished number; a
fork resolver chooses.

| Verdict | Meaning | Required content |
|---|---|---|
| **Determined** | the standard resolves it | edition + section citation |
| **Judged** | the standard does not resolve it; a reading was chosen | candidate readings, which is conservative, **what would change the choice**, who decides |
| **Insufficient basis** | the library lacks what this fork needs | the specific document to acquire |
| **Alternative means** | the resolution is less conservative than the declared basis permits | named as §104.11 territory, not applied silently |

*Alternative means* is top-level so it cannot hide inside a *Judged*.

Never soften a *Judged* into a *Determined*. A citation that does not settle the
question is research, not authority.

## 8. The record

### 8.1 Format

Generalized from `lgs-truss-designer/docs/EDITION-DELTA-S2-20-vs-S3-22.md`, which
already resolves a real fork correctly. That file is the model, not the Desktop
template.

Written to the **consuming repo** at `docs/judgments/JR-NNNN-<slug>.md`:

```yaml
---
id: JR-0001
clause: AISI S240-20 §E4.5.1
basis: AISI S240-20            # the full declared designation from code-basis.toml,
                               # e.g. "AISI S100-16 (2020) w/S2-20" — supplement included,
                               # because a clause number without one is unresolvable
repo: lgs-truss-designer
commit: <sha at resolution>
signals: [2, 3]
verdict: judged
decided_by: Carlos
date: 2026-08-15
pin: tests/test_gusset_layout.py::test_wrap_around_pair_is_adjacent
---
```

Body sections, in order:

1. **The fork** — one line
2. **Independent expectation** — recorded before research
3. **Candidate readings** — each with its consequence for the number
4. **Research** — citations with edition, section, and locator
5. **Resolution** — the reading chosen, the ladder rung that governed, and why
6. **What would change this** — the condition that would reopen the fork
7. **Not covered** — mandatory; what this record does *not* settle

Section 7 is what keeps the record honest. It is easy to write "resolved" and stop.

### 8.2 The pin

The record's `pin` field names a test in the consuming repo whose docstring cites
`JR-NNNN` and asserts the chosen reading. Reversing the reading fails the build and
points at the record.

Prose explains; the assertion enforces. This is the calcguard thesis applied to a
decision instead of to a quantity.

### 8.3 Vault copy

```
kb-note decision "<title>" --body "…" --project <repo> --source JR-NNNN
   → /mnt/nas/Projects/Documents/_vault/Inbox/YYYY-MM-DD-<slug>.md
   → 03:15 notes-sync.sh: kb-consolidate  Inbox/ → Decisions/
   → kb-ingest --source notes → `notes` workspace (bge-m3)
   → retrievable via `llocal research`
```

Verified live: last run 2026-08-14 03:15, `indexed=1 skipped=60 failed=0`.

Three facts the skill must state rather than assume:

- **`decision` is the correct type.** An unrecognised type falls back to `Findings`
  (`consolidate.py:64`).
- **Discovery runs through `llocal research`, not `vault-search`.** The catalog
  indexes the 4,269 PDFs; a `JR-` record lives in the `notes` workspace. Querying the
  wrong index returns a confident zero.
- **A record is repo-visible immediately, vault-discoverable after 03:15.** Same-day
  cross-project lookup needs a manual `kb-ingest --source notes`.

`Decisions/` does not exist on disk yet. Verify it on the first promotion instead of
trusting that it appears.

## 9. Layout and install

```
~/projects/calcguard/skills/engineering-judgment/
  SKILL.md                              trigger, signals, sequence, verdicts
  references/
    fork-signals.md                     the nine, each with its check and its receipt
    precedence.md                       ladder, conservatism rule, edition-delta protocol
    research-protocol.md                which command, in which order, and what never to use
    record-format.md                    record, pin, vault copy
    parked-project-mode.md              sealed-project material, parked
  assets/
    judgment-record-template.md
```

Installed by symlink, not copy:

```bash
ln -s /home/atomicjr/projects/calcguard/skills/engineering-judgment \
      /home/atomicjr/.claude/skills/engineering-judgment
```

`reference-library` was installed as a copy and silently diverged from its repo. A
symlink cannot.

## 10. Out of scope

Deleted from the Claude Desktop draft:

- the nine-element design-basis interrogation, which blocks every invocation in a repo
- ADVISORY / GATE modes — a demand-driven resolver has nothing to gate
- `superseded_by` and `adopted_by` frontmatter — the retired model, and hand-written
  metadata is not verification
- `vault_search.sh`, which greps PDFs
- `calcguard-input.schema.json` and the handoff section
- references to `architect-code-review` and `mep-engineer`, neither installed

**Parked, not discarded**, in `references/parked-project-mode.md`: permit-date
governance, state amendments, IEBC triggers, load path, serviceability against the
actual finish, and constructability. This material is correct for sealed project
work and worth keeping intact. It becomes a separate skill if and when that work
needs one.

## 11. Testing

A skill has no unit tests, so acceptance is a replay.

**Acceptance:** each of the six forks in §1, described from its original context with
the resolution withheld, must trip at least one signal in §5. A fork that passes the
scan is a missing signal, and the signal gets added.

**Negative control:** a clause that is unambiguous, fully specified, and oracled must
trip **zero** signals. Without this the list degenerates into "always fires", which is
the friction this design exists to avoid.

**First live run:** resolve one real open fork end to end — §7.6.1 or J4.3.1 in lgs —
and confirm the record commits, the pin fails when reverted, and `llocal research`
returns the record after the next sync.
