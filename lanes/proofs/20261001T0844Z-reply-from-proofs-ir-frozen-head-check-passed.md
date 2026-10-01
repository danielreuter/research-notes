---
id: 20261001T0844Z-reply-from-proofs-ir-frozen-head-check-passed
campaign: verity
lane: proofs
kind: reply
status: open
repo: danielreuter/verity
origin: proofs-ir (bc-6cd83494), re note:20261001T0728Z and note:20261001T0730Z
---

**The frozen IR head passed `check`.**

- **Branch and head:** `cursor/proofs-ir-95d4` at `46c768b2c3bf427373bd28e2346660acfb91eb83`, frozen as-is. Main had moved
  21 commits ahead without conflicting, so I merged nothing new.
- **Check run:** `r20261001-073736-9655` on vy-nebius-1, `uv run --extra torch-cpu python tools/check/check.py --record
  --on vy-nebius-1`, gpu 0. It finished at 08:43Z (1:43 AM PDT) with rc=0, SUCCESS, and the result valid and passed. All ten
  steps passed, and #642 (the Lean-audit scratch fix) wasn't needed:
  - `preflight-lock` and `preflight-lints`;
  - `pytest`, which took 3479 s (the vLLM TP2 MoE build that OOMs on a 15 GB VM passes there);
  - `circuit-check --all`;
  - `flock-circuit-build`, `lean-build`, `lean-unit-cut`, `lean-audit` and `lean-suites`;
  - `lean-agreement`, run against the pinned upstream build because the branch touches `backends/flock/`.
- **circuit-check report:** `art:8abc77ef909adaf8a13e00c9516ee13bb70935cd2a202facb9c76c939a6655d8`. It covers every
  Definition the branch adds or changes, all at `46c768b2c`, and has 0 failures over 21 targets:
  - the gates `And2_v1`, `Xor2_v1`, `And3_v1`, `Xor3_v1`, `Not_v1`, `Const1[0x0]_v1` and `Const1[0x1]_v1`;
  - `F2fpBf16_v2`, `AmpereBF16TcDot16_v3` and `HopperBF16WgmmaDot16_v2`;
  - `GemmCoordinate_v3` and `DotBf16_v3`, each on both steps at K = 64;
  - attention's seven softmax operations: `F32AddFtz_v3`, `F32SubFtz_v3`, `F32MulFtz_v3`, `F32FmaFtz_v3`,
    `F32FmaSubFtz_v3`, `F32Max_v2` and `GuardNegInfZero_v2`.

  The warnings are two unpinned lowerings (`And3`, `Xor3`) and redundant IR gates from the zero accumulator. The
  run's own `circuit-check --all` passed too.
- **No PR, per your note.** The IR is ready to land through `research merge cursor/proofs-ir-95d4`.

The ROM decision request in note:20261001T0503Z is **moot**: proofs-mufu builds each MUFU table as an interpolator
circuit, so no ROM representation is needed.

**Attention and FP8/FP4.** `cursor/proofs-ir-attn-95d4` is stacked on the frozen head plus proofs-mufu's
`1fd5cb6c3`. Its head is `8dbeb445f`, pushed, with circuit-check green at every commit:

- `Fa2InvSum_v2`;
- `AttnBlock_v6`, `AttentionHead_v6` and `Attention_v6`, FA2 attention on bits. Their word views are the v3 chain, and
  they agree bit for bit on random, special and overflowing inputs, including GQA;
- `Gemm_v3`;
- the E4M3 steps and `GemmCoordinateE4m3_v2`;
- `unit_fp4` moved into core as `verity.ml.boolean.fp4`.

Next are the Boolean NVFP4/MXFP4 steps and coordinates, then a recorded check of that head well before 6:15 AM PDT,
avoiding node 1's 5:05–5:55 window.
