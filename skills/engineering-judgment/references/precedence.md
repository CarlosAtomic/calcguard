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
