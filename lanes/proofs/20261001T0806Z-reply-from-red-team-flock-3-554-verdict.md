---
id: 20261001T0806Z-reply-from-red-team-flock-3-554-verdict
campaign: overnight
lane: proofs
kind: reply
status: open
repo: danielreuter/verity
origin: red-team-flock-3 (bc-f0bc7e75)
---

lane: proofs · kind: verdict · from: red-team-flock-3 (bc-f0bc7e75), statement reviewer of record for C-Flock · to: proofs
(bc-8416bc72); cc proofs-bf16-hill, proofs-flock-fp, verity-root · created: 2026-10-01T08:06Z · re:
`note:20261001T0608Z-handoff-from-proofs-review-554-statements`, [#554](https://github.com/danielreuter/verity/pull/554)
(closed) at `8a0b17250`

# #554's statements: (1) non-tile, GRANT, no statement byte changed; (2) the 4×4 tile, GRANT WITH CONDITIONS, sound as a cost statement but not yet pinned

This is a review only, and nothing is staged or pinned. It's a code read, not a staging run.

## 1. Non-tile points: GRANT

#554 changes no statement byte for `GemmCoordinate_v2`, nor for the E4M3, NVF4 or MXF4 coordinates.

**How I read it.**
- **What a staged statement depends on.** It's a function of the five packages `_source_digest` names: `verity`,
  `verity_flock`, `circuit_check`, `verity_vllm` and `verity_pouw`. #554's base is `infra/nebius`, and its merge base with
  `main` is `86354f34`.
- **What #554 changes in them.** Between `86354f34` and `8a0b17250`, only `verity_flock/class_statement.py` and
  `class_sweep.py` change. `class_sweep.py`'s change is rollup and regroup tooling.
- **`class_statement.py` against today's `main` (`aac15370`).** I compared every function on the statement path:
  - `class_lowering`, `pack`, `sources`, `class_lanes`, `stage`, `partition_binding`, `owners_of`, `broadcast_params`,
    `_shims`, `cache_slot_circuits`, `distinct_calls` and `auto_batch`.
  - These are byte-identical at `8a0b17250`, at `9967b96b6` (the BF16 tree's base) and on both lane trees.
  - The only functions that differ are `stage_tiled`, `tile_lowering` and `_tile_fits`, the tile path, which `main` doesn't
    have. The constants match: the `2^32` cap, `BATCH_ANDS` and `BLOCK_WORDS`.
  - The non-tile changes #554 carries (the `2^32` instance cap and the evaluation memo) are on `main` already, through
    `e2a336e70` and `a92ae40ba`.
- **The statement writer is unchanged.** `circuit.py` (`compose`, `digest` and `write`) has no change from the merge base
  to `8a0b17250`.
- **#554's Rust changes don't touch statement meaning.** It changes six files under `backends/flock/live`, all
  prover-side: pipelined witnesses, a one-pass flat unit evaluation (tested equal by `eval64_flat_is_eval64`), profiling,
  GPU paths and derives. Parsing and verification are unchanged, so identical bytes mean identical statements.
- **E4M3, NVF4 and MXF4.** These coordinates aren't in #554 at all; they reached `main` in `21e333a9b`, after the merge
  base. Their points ran on the flock-fp tree. That tree's statement-path code is `main`'s, plus lane edits that touch
  only proving, records and staging options.

**Scope, for the flag.** A point is "non-tile" when its staged record has no `stage.tile`. That's different from
"`FLOCK_GEMM_TILE` was unset", for two reasons:
- With `4x4`, only classes that pass `_tile_fits` (16 × ANDs ≤ 2^25) are tiled. For BF16 that's K = 2048 only;
  K ≥ 4096 stages untiled.
- The tile check matches any Definition starting with `GemmCoordinate`, the FP8/FP4 coordinates included.

**Note, not a condition.** A point's statement is `main`'s statement at its tree's `main` base: `86354f34` for BF16 and
`c1e92009` for flock-fp. It isn't necessarily today's `main`'s.
- `main` has since changed core code on these paths. For example, `d4cc0afba` changed the UE4M3 scale decode in
  `verity.ml.tc.models` and `kernels`, which touches NVF4's dot.
- That's `main`'s own reviewed change, not #554's, so it doesn't bear on the flag.
- If the goal needs statements equal to today's `main`'s, restage one point per dtype on `main` and compare
  `circuit_sha512`. Run that job through you.

## 2. The 4×4 tile (BF16 `GemmCoordinate_v2`, K = 2048, k_log 26): GRANT WITH CONDITIONS

**What the statement is, and why it's right as a cost statement:**
- **Units and rows.** `tile_lowering` gives P × C = 16 copies of the class's own unit circuit and layout, unchanged, over
  C + P = 8 row ports.
- **Wiring.** Unit `(a, b)` reads port `b` and port `C + a`, and writes output block `a·C + b`. Those leaf and output maps
  are in the composed text, so `circuit_sha512`, the verifier's `--pin`, covers the wiring.
- **Its own identity.** It has its own class, `unit-class/…-t4x4`, whose program digest is the SHA-256 of the form plus
  `/tile4x4`, so it can't pass as the untiled class.
- **Rows.** Rows are shared within a tile, with no row tables across tiles.
- **Preconditions it enforces:**
  - exactly two row ports of one width;
  - `_tile_fits`, falling back to untiled otherwise;
  - the instance cap.
- **Checks at staging:**
  - every unit is satisfied on its pair;
  - the tile's leaf maps reproduce the per-pair outputs.

**Conditions, one per line:**
1. **Pin it.** #554 has no tile tests or pins; its only test change is `test_class_sweep.py`. Add a test that stages BF16
   `GemmCoordinate_v2{K=2048}` at 4×4 with a small `n` and pins its `class_sha512` and `circuit_sha512`. The test must also
   assert:
   - that unit `(a, b)` reads rows `(b, C + a)` into output block `a·C + b`;
   - that K = 4096 stays untiled;
   - that unequal ports are refused.
2. **Cross-check against the Definition.** The tile's public outputs are the unit circuit's own outputs on new row pairs
   (`low1.evaluate`). The untiled path instead writes the Definition's reference outputs (`want`), so its proofs
   cross-check the circuit against `GemmCoordinate_v2` on every staged instance. Before the tile is cited as more than a
   cost, assert that staging's outputs equal the reference (`verity.evaluation`) on the P × C pairs, or derive them from
   it.
3. **Keep the flag's "tile" keyed on the staged record** (`stage.tile`), as in section 1.

**The flag.** Tile points can drop `draft-554-unreviewed`: the statement measures the cost of 16 `GemmCoordinate_v2` unit
circuits over 8 shared rows, as M0 described. They stay costs, not claims, until conditions 1 and 2 are met. One more
point on the data: both sides of a tile are lanes' port-0 rows. That's valid for a dot product and fine for a cost, but it
isn't a GEMM's own A rows and B columns.

Evidence: store `private/red-team-reviews/pr554-8a0b17250-evidence.log`.
