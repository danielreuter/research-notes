---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T23:20Z
---

# red-team-flock: the fp8-hopper (H100) and bf16-ampere (A100) layouts of verity/flock-pure-block/v2 (PR #30 @ 48045063) are both GRANTED WITH CONDITIONS at NON_ZK_PROOF. bf16-ampere also needs its lowering pinned in lowering.py.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "fp8-hopper and bf16-ampere layouts".
Selftest rerun: r20260925-230859-6d32, art:0f0b6f41. Pod terminated at 23:15Z; about $0.10.

## fp8-hopper (H100 E4M3)
- **Layout:** the reviewed fp8 layout unchanged. 1,536-byte rows are 1.5 chunks, so chunk 0 has 16 compressions and
  chunk 1 has 8, with END at block 7; 48 units of 32 E4M3 words each. The per-slot constants, c_in(0) = +0, the 4 CV
  regions and AccOut against the verifier's own `inst.out` are all generic in `out_cols` (c_out word 56). No epilogue.
- **Lowering:** the regenerated netlist sha equals PINS **904ca664**. It has 7,297 rows, all topological, with 65
  assertion rows.
- **Differential test:** 400 random units against `verity.ml.tc` HOPPER_E4M3_K32 (groups (32,), width 14, floor −139;
  the Pipe matches the model), with subnormals, zeros, max-normal operands and extreme accumulators: 0 mismatches.
- **Selftest (CPU, 48045063):** 16/16 at 8 and 64 VUs.
- **Bound:** 2^-195.54 per proof at m = 33, and 2^-195.44 at m = 34 or 35. One proof holds at most 16,384 VUs; larger
  batches are a union over sub-batches.

## bf16-ampere (A100 BF16)
- **Layout:** the reviewed bf16 layout unchanged (blocks per (VU, chunk), 96 units of 16 words, committed cross-chunk
  accumulators, Y region). The unit fits: useful 8,065 ≤ 2^13, const at 8,064, c_out word 61 and y16 word 62, whose
  regions fall at bits 7,808–7,951 < 8,192.
- **Lowering:** the Pipe `("bf16-ampere", BF16, (8, 8), 25, −132, epilogue, AMPERE_BF16_M16N8K16)` matches
  `verity.ml.tc.models`. The regenerated netlist sha is **e97ecb9e f01d653b 550ebe94 7cc12d92 c6039261 3457b560
  246b99af f4922247**, the same as flock-gpu-link's. 8,065 rows, all topological, 33 assertion rows.
- **Differential test:** 400 random units against AMPERE_BF16_M16N8K16, including the f32_to_bf16 epilogue, with
  subnormals and extreme exponents: 0 mismatches.
- **Selftest (CPU, 48045063; instances from `instances.write` with the entry patched in):** 18/18 at 8 and 64 VUs.
- **Bound:** 2^-195.44 per proof (m = 35 at 8,192 VUs/proof).

## Conditions (both layouts, as for fp8-ada)
- **PB1:** each result names the verifier commit and binary. The verifier path must equal 48045063 (e5d54118, a6a6e548
  and d93ce18b are all equivalent).
- **PB2:** the bound is a union over sub-batch proofs.
- **PB3:** a non-producer replay labels `verified`.
- **PB4:** records carry `link_mode` exchange, `require_link` true, and the cell's Σ.
- **FA1:** a separate-pod verifier serving its own instance files. Today's evidence for both layouts is loopback.
- **FA2 (hardening):** fp8 negatives for c_in(0) and the output word.
- **For bf16-ampere only, AM1:** flock-backend adds the Pipe and **PINS["bf16-ampere"] = e97ecb9e…** to
  `verity_flock/lowering.py`, and the cell's verifier runs with that pin (`--pin`, `lowering_sha256` in the result).
  Until then the lowering is unpinned, and a bf16-ampere cell isn't admissible.

When flock-backend routes the cells, I'll check PB1–FA1 (and AM1) and label them `NON_ZK_PROOF`.
