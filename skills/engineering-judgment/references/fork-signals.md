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
| 3 | **Ambiguous scope** | a term or a scoping statement admits two readings that change the number — a word like "adjacent", "continuous", "supported", "effective", or two clauses whose applicability overlaps for this member | `joint_leff`; E2.2 vs E2.3 |
| 4 | **Referenced artifact unread** | a figure, table, or appendix is cited and has not been opened | ASCE §7.6.1 figure |
| 5 | **Determination handed to you** | the clause states who decides instead of what the answer is, deferring to the implementer — "by rational analysis", "by test", "engineering judgment is required", "by accepted engineering principles" | S240 §E4.5.2 commentary |
| 6 | **No oracle** | no worked example, no independent tool, no closed form for this branch | §7.6.1, J4.3.1 |
| 7 | **Cross-table pairing** | two limits from different clauses are combined; is the pair legal? | the 1.43× unconservative pair |
| 8 | **Edition delta on the path** | material from an edition other than the declared basis is in play for this clause — a worked example, figure, commentary, errata, or value you are reaching for — whether or not a difference is yet known | S2-20 vs S3-22 |
| 9 | **Outside tested range** | a listing or equation is applied beyond its validated span, thickness, or spacing | Whitmore on CFS plate |

## Notes on the ones that mislead

**Signal 3 is about scope, not vocabulary.** A single ambiguous word is the obvious
case. The harder one is two clauses whose applicability overlaps for the member in
hand, where the standard's scoping language does not assign it to either.

**Signal 4 is about what you have opened, not what you have read about.** A figure
summarised in a preface is not a figure you have read. ASCE §7.6.1's prose was
identical across two editions while its figure gained a √Is term and a cap.

**Signal 5 is not limited to a fixed phrase.** Any construction in which the standard
declines to supply a rule and hands the determination over is this signal — including
commentary that says engineering judgment is required. The tell is that the clause
tells you *who decides* instead of *what the answer is*.

**Signal 7 fires on correct inputs.** Both values can be read perfectly from their own
tables and still not be combinable. Mutation testing cannot find this, because every
mutation is on the wrong axis — it perturbs the values, not the pairing.

**Signal 8 fires when you reach for another edition, not on a proven difference — and
not on its mere presence on the shelf.** The library holds many editions of most
standards; if simple existence tripped this, it would fire on every clause and become
a tax. The trigger is that something from a non-declared edition is actually in play
here: a worked example you want to use, a figure you are reading, a commentary, an
errata. Then go and diff — and the diff is evidence, not a verdict. A newer edition
does not invalidate the declared one, and is frequently narrower. See `precedence.md`.

**Signal 9 cuts both ways.** Outside the tested range a listing is *silent*, not
permissive. Drop back to the general provision rather than extrapolating.
