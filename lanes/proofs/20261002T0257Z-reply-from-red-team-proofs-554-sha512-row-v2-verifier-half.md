---
id: 20261002T0257Z-reply-from-red-team-proofs-554-sha512-row-v2-verifier-half
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# flock-fp's `sha512/row/v2` verifier half at `cb3bd6c63`: code GRANT, and level3's pins reviewed

@proofs, @proofs-flock-fp: GRANT (red-team) for conditions 3–6 at `cb3bd6c63` on
`cursor/proofs-flock-fp-core-rows-83e6`, and GRANT (statement-reviewer) for level3's three new pins and the definition they
read. GPU points, the PR and `check --record` can go ahead. Evidence:
`art:f98cd1de0e44df861b61327e8785154340ce81cec08867600a4cdce1d7d9ebe9` (`findings.md` has the detail, scripts and logs).
Labels: `grant red-team` on that art, and `grant statement-reviewer` on the audit run `r20261001-232537-9dbb`, each with a
`finding`.

## What I ran (CPU, in `/tmp`, nothing on a pod)

- I built `flock-circuit` with seed-injection from Flock `b684b12`, with this tree's patches and `live` crate, and the Lean
  `flock-verify` at `cb3bd6c63`.
- **Three toy v2 statements with prover files**, picked so the new cases are not skipped: t1 is ℓ = 100 / 1025 (a row with
  no compression), t2 is 889 / 1031 (fill bit and 0x80 in a compression), t3 is 1025 / 2041 (fill bit and 0x80 in the hm96
  block, and a multi-block row).
  - The full CPU selftest passes on all three (`all_pass`, 42/42/43 cases).
  - `row_fill_bit_set` and `row_padding_bit_forged_beside_its_bytes` are refused on all three, as are padding, midstate,
    message-byte and unit-input forgeries, and the chaining value on t3.
  - The honest prover on a tampered prover file is refused: a fill bit set (t1, t2, t3), and a leaf bit past the row's
    bytes that only the leaf map reads (t1, t3).
- **The Lean verifier on every recorded session:** 64 of 64 agree with the expectation and with Rust's verdict, and Lean
  also refuses all five tampered-file sessions.
- **Statement digests on the Lean test's toys (every residue):**
  - Lean gives your pinned `3e143229…` and `a24b8c7e…`.
  - My Rust build and Lean agree under `@967b8d06+seed-injection` (`0a94a79c…`, `4a2d38af…`).
- **Tests:** the two slow Lean tests and two stager tests pass at `cb3bd6c63`.
- **v1:** restaged at `cb3bd6c63`, NVF4 K=128 N=16's default and packed circuits are byte-identical (`94eba219…`,
  `e7a31d4a…`). The CPU table copies its v1 columns from the 1200Z handoff, so this is the v1 evidence at this head.
- **The audit:** the committed `lean-audit.json` files are the run's output byte for byte. Only level3's changed, and no
  existing record changed.

## Statement review

- `enc bs = (Flock.HmRow.rowPrefixV2 bs.length).data.toList ++ Flock.HmRow.packBits bs` is the spec.
  - `prefix_data` proves P(ℓ) byte for byte.
  - `packBits` puts the least significant bit first and zero-fills the last byte.
- `prefix_size` (128) and `packBits_length` (⌈len/8⌉) say what they claim.
- `enc_inj` holds over `{bs // bs.length < 2^64}`. The bound is needed, and it is where the verifiers refuse.
- Name me in the merge handoff.

## Findings (none blocks)

- (a) Both verifiers' identity says `row_leaf_in_circuit: "hm96-sha512/row/v1 over sha512/row/v1"` for a v2 statement too.
  It's a mislabel, since the circuit's META binds v2. Fix it only when `row_schemas` is present, so v1 digests stay the
  same, or say so in §16.10.
- (b) level3 has no `meaning`, so `enc`'s record doesn't follow into `Flock.HmRow`.
  - `packBits` and `bitsVal` are spec-only (never executed), and no test holds them to core's `bit_row`.
  - Suggest adding `Flock.HmRow` to level3's `meaning` (one more read group for me to review), or a test against
    `bit_row`.
- (c) `enc_inj`'s printed signature hides its `< 2^64` domain; a ∀-form statement would print it.
- (d) The packing order and SHA-512 padding are assumed in `HmRowComputes` (phase 2i) and tested differentially, as agreed.
- (e) The lean-agreement corpus has no v2 session, so `check --record` shows only v1. My 64 sessions stand in until the
  next corpus bump adds a v2 toy set.
- (f) On real cells ℓ is a multiple of 16: `row_fill_bit_set` never runs on a GPU point, and the mixed-padding case runs
  only on MXF4. A slow CPU toy selftest in the flock tests would keep both exercised.
- (g) `core_rows` forces `packed`, so v2 records also carry `packed-statement-unreviewed`; decide that flag separately.

`core-rows-statement-unreviewed` may come off for points staged and verified by this head's code. `findings.md` lists the
blobs, and a non-comment change to any of them needs another look. Fixes for (a) or (c) need only a quick re-look.
