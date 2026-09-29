---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: finding
from: flock-netlist / M0 (bc-ff572e70)
to: red team (M0 statement review), via the research coordinator
created: 2026-09-28T01:25Z
---

# M0 on main: what changed in PR (a) #192 and PR (b) #193 against the reviewed #83 `73a273d4`, for re-grant

- **(a):** the circuit prover with inline reads, [#192](https://github.com/danielreuter/verity/pull/192).
- **(b):** the multi-table statement, [#193](https://github.com/danielreuter/verity/pull/193), stacked on (a).
- **Base:** `main` `df3bc5e1`, which is train K with #104, #125 and #140.

## 1. The `verity/flock-circuit` statement did not change

These are byte-identical to `73a273d4` on (a):

- `live/src/circuit.rs` (`Composite::parse`, `Stmt`, the digests);
- `lookup.rs`, and the session in `lib.rs` (coins, records, replay);
- the backend identity and tags in `flock-circuit`;
- `verity_flock/circuit.py`, `sha512_circuit.py` and `tail.py`, apart from the helper below.

The only other Rust changes in (a) against `73a273d4`:

- **The selftest harness.** `unit_input_differs_from_its_message_bits` now flips unit 0 when a block holds one unit, so the
  case can no longer prove an honest witness.
- **The glue moved to (b).** Nothing in the prover read it.
- **`ir_tail.rs`.** `main`'s one-line ex2 clamp (#137), in the tail verifier of the frame statements. The circuit statement
  doesn't use it.

(a)'s statement is the Lean verifier's `Tags.circuit967b8d06` tag set.

## 2. Every template's pinned circuit changed, only in its unit

Train K's lowering (#104's hash-consing and NaN-payload-exact pieces, #140) makes smaller unit circuits. Per captured slice,
comparing each CIRCUIT section's SHA-256 against `73a273d4`:

- only the `unit` section differs;
- every tail stage, the `sha512x3` compression slot and the `hm96` row slot are byte-identical (checked on attention and
  rmsnorm-fused, the two templates with in-circuit tails).

| captured slice | unit ANDs, `73a273d4` → (a) | circuit pin (SHA-512), `73a273d4` → (a) |
|---|---|---|
| attention-head fa2 d64 bn128 | 8,623 → 8,260 | `2b2e96039554…` → `441f12f6b4f1…` |
| gemm-coordinate k2048 | 8,623 → 8,260 | `cecaa76ade94…` → `c510bb42c720…` |
| gemm-coordinate k8192 | 8,623 → 8,260 | `862800f29c71…` → `cc8e074739fc…` |
| rmsnorm-fused-cuda n2048 | 317,334 → 308,358 | `d1fa4195739d…` → `d037ef3ada9c…` |
| rmsnorm-triton n2048 | 1,132,502 → 1,114,422 | `d7987c8f23d3…` → `2d443db7ae8b…` |
| rope-head d64 | 5,996 → 5,828 | `0e7e078632da…` → `d2dafe7efdde…` |
| silu-mul i8192 | 5,398 → 5,212 | `7f919e3553a0…` → `b3d0f6c23aaf…` |

Full digests are in PR #192's body.

- **What this means for grants.** The granted cells `art:e352f2ad` (attention) and `art:a83371c2` (GEMM) pin #83's circuits
  at `855fe81f`. They remain evidence for those circuits. A Table 1 row citing the merged prover needs cells re-recorded at
  (a)'s pins.
- **The units' correctness** against the IR rests, as before, on `circuit-check`. `check`'s `circuit-check --all` runs on (a)'s
  head.

## 3. New in (a): table reads inline, as plain rows of the unit

`ir_lower.layout` now lays out a `gf2` table read (`C.lookup`), which it refused before. It uses §1's construction (low and
high decoders, product rows, copy rows) inside the unit's own rows, with no slot and no wires.

- **C1.** It holds without anything to check: an inline read has no late input and no index wire.
- **Forced rows.** Every row reads only earlier rows, the index forms or the pinned constant. Tests check this on random
  tables and on the pinned rcp read (34,728 rows, 143,860,467 set bits).
- **Selftests.** On inlined classes (1 ex2, 1 rsq, and rcp plus sqrt), `unit_internal_bit_flipped` and
  `unit_input_differs_from_its_message_bits` are refused, and the full 31 cases pass on the ex2 class. Measurements are in
  `internal/lanes/coordinator/20260927T2045Z-answer-flock-netlist-m0-inline-reads.md`.
- **Not added:** a negative that flips a read's value and carries it downstream. M0 publishes unit outputs, so it would
  usually be refused on the output claim.
- **Unchanged:** the attention template's tail still places its reads in the reviewed lookup slots, so its tail sections are
  unchanged.

## 4. Neither statement changes

- **`tail._f32_div`.** #140 removed `fp.f32_div_const`. The tail keeps the same exact-reciprocal multiply, and its stage
  sections are byte-identical (above).
- **`circuit_bench` fingerprints** record `Lowering.domain`, which is `total` unless the unit asserts, in place of the old
  hardcoded `"finite"`. That is a recording field only.
- **(b) `verity/flock-tables`.** Its files are byte-identical to `73a273d4`.
