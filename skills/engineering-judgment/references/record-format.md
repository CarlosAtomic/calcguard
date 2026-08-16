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
repo: <the repo this record lives in — NOT copied from this example>
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
