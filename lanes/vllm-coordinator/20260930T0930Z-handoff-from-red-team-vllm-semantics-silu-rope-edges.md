---
id: 20260930T0930Z-handoff-from-red-team-vllm-semantics-silu-rope-edges
campaign: overnight-sep30
lane: red-team-vllm-semantics
kind: handoff
status: open
repo: danielreuter/verity
origin: red-team-vllm-semantics
cursor:
  subagentId: "bc-05c0bb3e-507d-57b1-ae79-cac14d00af0d"
---

# `silu-edge-cases` rated broken, with two new causes; `RoPE_v1`'s hi contraction is the wrong one on sm_120

Labels are on `r20260930-092038-7dbc` (sm_120, vLLM d9105ea80). The first pass was `r20260930-082720-fca5`. Probe: `scripts/red-team-vllm-semantics/edges2_probe.py`.

## SiLU (broken at the edges, as the table already says)

The three known classes reproduce: NaN words (0x7FFF vs 0x7FC0), gates below −88.7 (the GPU gives ±0, `SiluMul_v1` a subnormal), and gate −0 (the GPU gives −0).

Two causes are new:

- **`up = −0`.** `csrc/libtorch_stable/activation_kernels.cu` at d9105ea80 computes `ACT(gate) * ((float)up + beta)` with `beta = 0.0f`, on both the vec and scalar paths. So `up = −0` enters as +0, and the product's zero has the other sign: 65,279 of 65,536 gates at `up = 0x8000`. The model `mid * (up + 0.0f)` removes all of these.
- **Gate −inf.** It gives NaN (`-inf/(1+inf)`), where the model gives −0.

Reproducer: `silu_and_mul` on the row `[g=0x3F80 | u=0x8000]`. The GPU gives 0x0000; `SiluMul_v1` gives 0x8000.

Finite ordinary gate and up words are exact.

## RoPE (rated conditions; the row's rationale needs correcting)

`|cos|,|sin| ≤ 1` is not sufficient. The failures come from products that underflow f32, not ones that overflow.

- On sm_120 the lo half is `fma(x, c, -RN(y*s))`, as `RoPE_v1` has it. The hi half is `fma(x, s, RN(y*c))`, not `RoPE_v1`'s `fma(y, c, RN(x*s))`. Every recorded mismatch is at d ≥ 64 and equals the latter form.
- Reproducer: head dim 128, is_neox, j=47, x=0x0014, y=0x8009, cos=0xB201, sin=0xB43A. At output d=111 the GPU gives 0x8000; `RoPE_v1` gives 0x0000.
- Some cases also differ in magnitude, for example x=0x045C, y=0x09C0, cos=0x37A9, sin=0xB09D at output d=76 (j=12): the GPU gives 0x01FD, `RoPE_v1` gives 0x01FE.
- With a real cache (base 1e4, 4096 positions) and activations down to 2^-133, 0 of 6.3M words differ. The table's "real cos/sin cache" condition is therefore right in practice.
- Cheapest fix: swap the hi contraction in `RoPE_v1`. It is exact for all non-underflowing inputs either way.
