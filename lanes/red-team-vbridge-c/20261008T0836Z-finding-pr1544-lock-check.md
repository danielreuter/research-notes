---
id: red-team-vbridge-c/20261008T0836Z-finding-pr1544-lock-check
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: verity
origin: [pr:1544@c128f603a6e49b4d10204407a6019581723750eb]
---

# Red team lock-only check of #1544 at `c128f603a`: grant

#1544 ("Lean gates") touches one file on the red-team rule's paths, `verity/core/service/flock/lean-audit.json`. The
lock's change regroups the `reads` records and does not change what C-Flock's verifier proves or records. Main is
`9bc787321`, which is also the merge base.

## The diff

- `git diff 9bc787321 c128f603a` changes no `.lean` file anywhere under `Security/`, `verity/core/service/flock/` or
  `verity/ml/flock/`. The only `.lean` file it changes is `tools/verity/lean/Facts.lean`. Since the records commit
  `ab8a09d09`, no `.lean` file under `verity/core/service/flock/` has changed.
- In the verifier lock, every section except `reads` equals main's. The one assumption,
  `Flock.Firewall.Contract.FirewallComputes`, has digest `0c8b7fe4…`, equal to its entry in the
  `Flock.Firewall.Assumptions` reads group.
- `reads` has the same 7 groups, each with the same readers. Two groups change: `Flock.Field` and
  `Flock.Firewall.Contract`, exactly as @proofs listed.
- The head's `reads` equals what `3d81b4502` recorded, and the lock written by the records run `r20261008-035245-eed9`
  (at `ab8a09d09`, audit passed). That lock differs from the head's only in `assumptions` (#1548). Main's differs from
  `ab8a09d09`'s only in `assumptions` too.
- `guarantee_reads`, `read_groups`, `group_keys`, `parent`, `digest` and `module_digest` are identical in `check.py` at
  `ab8a09d09` and at the head.

## The rule

`64b4fb78c` and `ab8a09d09` change which record each read constant is hashed in, not which constants are read.

- `group_keys` puts each read constant in exactly one record: its declaration's, when that declaration is read in the
  same module and reaches it through its own generated constants (`own`), and otherwise a record of its own.
- `digest` hashes each member's name, kind and SHA-256, so every read constant is still hashed.

From `eed9`'s `facts.json`, the verifier's guarantees read 153 constants:

- Grouped by parent, the old rule, they give exactly main's record names.
- Grouped by `group_keys`, they give exactly the head's.

The rehashes go the other way from "a digest covers more". `F128` is now hashed with only `F128.mk`; `By` and `Item`
alone; `scheduled` and `streams` with their own `match_*`. The `casesOn`, `rec` and `_sparseCasesOn_*` constants that
other definitions' matches reach have become records of their own. Coverage is unchanged: no read constant is in no
record.

## `instReprBy.repr` → `instReprBy.repr.match_1`

- Before, the record named `instReprBy.repr` hashed one constant, the matcher `instReprBy.repr.match_1`, grouped there by
  parent name. Its digest `2574e8ae…` is unchanged because the member set is unchanged.
- `instReprBy.repr` itself, the printer that `deriving Repr` (`Contract.lean:71`) generates, is read by no guarantee under
  either rule. It is not among the 153 constants, so no coverage is lost; the record was named for a declaration it never
  hashed.
- The matcher is reached as a shared matcher. `By.name` (`Contract.lean:73-78`) is a five-way match of the same shape,
  and its `own` list is empty, so it has no matcher of its own. It is read in the `Flock.Firewall.Contract` group by all
  six `holds_*` guarantees.

## Label

`pr:1544@c128f603a6e49b4d10204407a6019581723750eb grant red-team`, by `red-team-vbridge-c`, referencing this note.
