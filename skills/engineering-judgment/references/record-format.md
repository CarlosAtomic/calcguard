# The record, the pin, the vault copy

## Where

`docs/judgments/JR-NNNN-<slug>.md` in the **consuming repo** — the repo whose code the
decision governs, not this one. It travels with the code and shows in the diff.

Next id: the highest `JR-` in that repo's `docs/judgments/`, plus one. Start at
`JR-0001`.

### Numbering is per repo — so always say `repo/JR-NNNN`

Ids restart at `JR-0001` in every repo. `lgs-section-designer/JR-0001` and
`lgs-truss-designer/JR-0001` are **different records about different clauses**, and
both are correct.

**Qualify whenever the reference can travel** — prose, commit messages, handoffs,
memory notes, anything said across repos. Inside a repo's own files (a test docstring,
that repo's HANDOFF) a bare id is already scoped and fine, though qualifying costs
nothing and survives being quoted elsewhere.

| write this | not this |
|---|---|
| `lgs-section-designer/JR-0001` | ~~`JR-0001`~~ |
| `lgs-truss-designer/JR-0002` | ~~`JR-0002`~~ |

The `id:` field inside a record stays bare — it is already scoped by the file it lives
in, and `repo:` names the owner. Qualification is for **referring** to a record from
anywhere else.

> This rule was earned on 2026-08-16. A pending record for AISI S100-16 §J4.3.1 in
> `lgs-truss-designer` was discussed as "JR-0001" for a whole session while a different
> `JR-0001` already existed in `lgs-section-designer`. The result was a confident report
> that no judgment records existed when two did, and that the skill had never been used
> when it had been used twice. The collision is guaranteed to recur as more repos gain
> records — the naming is the cheap fix.

To find every record across all repos:

```bash
find ~/projects -path '*/docs/judgments/JR-*' | sort
```

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
export KB_NOTES_ROOT=/mnt/nas/Projects/Documents/_vault   # required; kb-note errors without it
/home/atomicjr/projects/spark-powerhouse/ingest/.venv/bin/kb-note decision \
  "lgs-truss-designer/JR-0001 AISI S240-20 E4.5.1 gusset adjacency" \
  --project lgs-truss-designer \
  --source lgs-truss-designer/JR-0001 \
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
  /home/atomicjr/projects/spark-powerhouse/bin/notes-sync.sh
  ```

  Use the script, not a bare `kb-ingest`. It sources its own environment;
  `kb-ingest` on its own dies on a missing `KB_SOURCE_ROOT`, and `kb-note` needs
  `KB_NOTES_ROOT` exported. Verified 2026-08-16: the script promotes Inbox →
  `Decisions/` and indexes into the `notes` workspace in one step.

`Decisions/` may not exist yet. Verify it after the first promotion rather than
assuming it appeared.

## Consult before deriving

Before resolving any fork, check whether it is already resolved:

```bash
llocal rag notes "<clause> <the ambiguous term>"
ls ~/projects/*/docs/judgments/ 2>/dev/null
```

A fork resolved once should never be re-litigated.


---

## The lint — did the research actually happen?

A record is a **learning artifact**. Its value is the research it forced, not the
paperwork it produced. The engine does not guess and does not give up: it reformulates
the problem, goes to the sources, and applies existing knowledge. Nothing is invented.

`acceptance/lint_records.py` checks for evidence of that loop:

| Check | What it means |
|---|---|
| the pin resolves to a **real** `def test_…` | the decision is actually held |
| a citation **shape** — `§`, `p. N`, `ESR-N`, `S100-16`, `CS-0125` | a source was opened |
| `judged` records enumerate candidate readings | the problem was reformulated |
| "What would change this" is filled | the premises are falsifiable |
| "Not covered" is filled | the record stays honest |

```bash
python skills/engineering-judgment/acceptance/lint_records.py          # every record
python skills/engineering-judgment/acceptance/lint_records.py <repo>   # one repo
```

**The pin check is the load-bearing one.** A record whose pin names a test that no
longer exists claims an enforcement it does not have, and nothing else notices — the
suite still passes and the record still *looks* pinned. Found exactly that on
`lgs-truss-designer/JR-0002`, whose pinned test had been renamed.

**Run it in the repo that owns the records**, not in calcguard. calcguard unit-tests the
lint itself; making its suite depend on another repo's record state would turn it red
for something it cannot fix.

`verdict: draft` is legal — research done, code has not moved. A draft needs no pin and
must not be cited as settled.
