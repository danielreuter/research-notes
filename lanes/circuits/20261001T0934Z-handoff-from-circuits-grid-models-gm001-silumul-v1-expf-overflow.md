---
id: 20261001T0934Z-handoff-from-circuits-grid-models-gm001-silumul-v1-expf-overflow
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits: gm001's replay failure is SiluMul_v1's expf-overflow edge; the quarantined SiluMul_v2 matches

This follows up the open question in note:20261001T0901Z-report-from-circuits-grid-models-counts-0205. I did the dive on my own VM
from the 27 MB slim keep, without touching node 1.

**Finding.** It is a gap in the Definition, not a fault in the Commit:

- cov-gm001 is `qwen3-06b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__greedy__bi-eager`. It fails at
  `model.layers.27.mlp.act_fn`, request r0, prefill step 0, row 15, element 107.
- The gate is `0xc2c2` (-97.0) and the up is `0x4183` (16.375). The GPU committed `0x8000` (-0): `expf(97)` overflows f32, so
  vLLM's `silu_kernel` gives `g / inf` = -0.
- The registered `SiluMulBf16_v1` gives `0x8010` instead (a tiny `g·e^g` times u).
- The quarantined `SiluMul_v2` / `SiluMulBf16_v2` (lane vllm-coverage-defs: `_C.silu_and_mul` on the red-team's sm_120 edge words,
  labels on r20260930-092038-7dbc `silu-edge-cases`) equals the committed row in all 3072 elements. v1 differs only at element 107.
- The other 459 of the 460 sampled VUs are equal.
- The window is narrow. That row's most negative gate, -140, gives -0 under v1 as well, because `g·e^g` underflows. Only gates from
  -89 down to about -103 produce a nonzero v1 word.

**Why it matters:**

- This is the first field occurrence I know of for that red-team edge. Any row with a large negative gate in that window (Qwen3's last
  layers here) fails the same way until `SiluMul_v2` is admitted.
- The replay samples 460 of about 274k VUs, so other rows will hit it at random. That is evidence for vllm-coverage-defs' admission
  of `SiluMul_v2`, if you want to forward it.
- The label on gm001's replay attempt now names this cause (`ov.note`, `labeller/causes.json`).

**Reusable check.** `labeller/silu_check.py <key>` in my lane fetches a row's slim keep and replay record and tests every SiluMul_v1
mismatch element by element against v1 and v2. I'll run it on every SiluMul_v1 failure the grid produces and label each one with what
it shows.

**Not done, and your call:** rerunning gm001's row once `SiluMul_v2` is in the tree. That would be a new key, never gm001 again.
