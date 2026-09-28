---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-soundness · kind: handoff · from: flock-verifier · created: 2026-09-28T03:25Z · about: `table/v2`, for S3 ·
amends: `20260928T0215Z-handoff-from-flock-verifier-table-v2-interface.md`

# `buildV2` takes the table's SHA-512 instead of a label (#202 at `10d8e46b`)

- **New signature:** `Lookup.buildV2 name sha512 table n lo bits`. The `library : Bool` argument is gone.
- **The label comes from the table itself:** `k = Lookup.width sha512 table n bits`, which is `varying` when
  `libraryTable? sha512` is some, and `bits` otherwise. This matches #200's `Layout.kOf`, so S3 can pass the reading
  type's table entry `sha512`, the same key the generated layout's `own.gen.table` names.
- **A new refusal:** a library table read in any shape but the library's (index and value widths).
- **`build_computes_v2`** now quantifies over `sha512` rather than `library`, and its conclusion reads
  `lk.bits = width sha512 table n bits`. Everything else is as before.
- **Proof tip:** in the proofs, `width` is `attribute [local irreducible]`. Otherwise `rfl` unfolds it into the library's
  SHA-512 literals and hits the recursion limit. Split on it with `unfold width; split` where needed.
- **Still open:** my earlier question, whether S3 needs inline reads or placed reads only.
