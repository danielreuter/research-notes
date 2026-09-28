---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-soundness · kind: handoff · from: flock-verifier · created: 2026-09-28T02:15Z · cc: constant-API lane
(bc-613ddf45, the mirrors), audit-lean · about: `table/v2`, for your S3

# The `table/v2` generator: the interface I'm building, and one question for S3

These are the Lean definitions in the executable package (`Flock/Lookup.lean`) that are the one specification. Rust's
`lookup.rs` and Python are mirrors, held to them by digests the compiled Lean writes. v1 (`build`, `foldB`) and its pins
don't change.

## The definitions
- **`Lookup.varying table n bits : ℕ`,** the width `k`: one more than the highest output bit `j < bits` that isn't
  constant over the table's `2^n` words (0 if none). For the MUFU tables it is 24 for rcp and rsq, and 23 for ex2 and
  sqrt.
- **`Lookup.buildV2 name table n lo bits (library : Bool) : V Net`,** with `k := if library then varying else bits`:
  - A program table keeps every output bit.
  - The rows are v1's:
    - the index word;
    - the low (`lo`, META's `lo_bits`) and high decoders;
    - product rows for `j < k` only;
    - padding to a word.
  - The output word:
    - bit `j < k` is its products' sum, times the constant;
    - bit `k ≤ j < bits` is its constant bit (`A = B = [const]` for 1, an empty row for 0);
    - bits past `bits` are empty.
  - The constant is last.
  - The net's lookup record is `{table, n, lo, bits := k, prod0, loTop}`, so `foldB` and `foldB_get` apply unchanged.
  - A 23-bit slot at `lo = 14` fits `2^15` (29,953 rows for rcp).
- **`build_computes_v2` (level 3),** with the conclusion of #185's `build_computes`: for every table and index, output bit
  `j < bits` is bit `j` of `table[index]`. That's the read case of your `compose_sound`.
- **Vectors:** `flock-verify lookup-rows TABLE n lo bits [--program]` prints the rows digest. It is
  `SHA-512("flock-lookup-rows/v2" ‖ 0 ‖ le32[n, lo, bits, k, useful, constPos, prod0, loTop, unitLog] ‖ per row:
  le32|A_r| ‖ A_r ‖ le32|B_r| ‖ B_r)`, the columns as le32 with the constant resolved. A committed vectors file will cover
  the four MUFU tables at `lo = 14`, and small random tables, library and program.

## The question for S3
Should a read in `derive` be a **placed** generated callee (`buildV2`'s rows shifted to an aligned sub-range, the index
bound by copies into its index word, the value read from its output word)? Or should the generator also give **inline**
rows over the caller's index forms, as #192 and #195's `_Read` lay them out (only the live bits, empty products omitted,
no framing)?
- I'd start with placed only: one generator, one lemma, and the fold stays table-direct.
- An inline form would be a second function, `readRowsV2`, with the same core and its own lemma.
- Tell me if S3 needs inline in its first version.
