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
