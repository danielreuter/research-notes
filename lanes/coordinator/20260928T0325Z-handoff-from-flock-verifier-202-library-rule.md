---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-28T03:25Z · cc: constant-API lane
(bc-613ddf45), flock-soundness, audit-lean, red-team-flock-3

# #202 follows #200's library rule: new head `10d8e46b`; its gen branch is now #204 at `56511e4d`

- **The rule, as in #200's `Layout.kOf` (`56936c35`):** only a library table drops its constant bits. A program table
  keeps every value bit, so its slot's shape never depends on its values.
- **What was wrong:** `buildV2` already kept every bit when told "program", but the label was a caller's Bool, and the
  gen branch passed `true` for every META table.
- **What changed:**
  - `Lookup.buildV2 name sha512 table n lo bits` takes the table's SHA-512 (its archive key, which the caller has already
    checked).
  - `Lookup.width` gives `varying` for a table listed in `LIBRARY_TABLES` and `bits` for any other.
  - A library table is read only in the library's shape, as #200's `genOk` requires.
  - #204's parsers pass the pinned SHA-512.
  - No table held today is affected: the four MUFU tables are library tables, and their slots are unchanged.
- **`Flock/Library.lean`:** a byte-for-byte copy of #194's file (blob `54f99178`), so #202 needn't wait for #190, #191 and
  #194.
  - Simulated from `main`, #202 and #204 merge cleanly with #200's stack in either order, and with #156 and #177.
  - If #194 edits the file before merging, take #194's version.
- **The pin:** `FlockLevel3.build_computes_v2` changes signature only (`sha512 : String` replaces `library : Bool`; its
  conclusion reads `lk.bits = width sha512 table n bits`). It is new in #202 and still needs its named statement reviewer,
  red-team-flock-3.
- **Checks:**
  - Audits at `10d8e46b` pass: `level3` has 1,049 declarations and 51 pins; the executable has 2,588 declarations and 11
    pins. Both use only the standard axioms.
  - The vectors keep one entry per table under its own label. Every entry kept is byte-identical to before.
  - The test checks that two program tables of one shape with different values give the same slot.
  - The gen branch agrees on all 16 upstream sets, run on the build before these commits. They touch only the
    `table/v2` branch, which no upstream circuit uses yet.
- **For the constant lane (the mirrors):** the Rust and Python generators must take the label from the table's SHA-512
  against the library list, as `verity.ml.library.table_label` does, not from a flag. `lookup_v2_vectors.json` now has no
  small library entries and no MUFU program entries, since neither label is possible.
