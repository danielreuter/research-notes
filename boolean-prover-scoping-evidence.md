---
cursor:
  subagentId: "bc-6e272646-640d-5431-b27a-72632487ad8b"
---

# Evidence for docs/boolean-prover-scoping.md

This note backs [the scoping doc](../docs/boolean-prover-scoping.md). No pods were used, and $0 was spent.

## AND counts from the current lowering

**How they were made.**
- Repo `main` in this cloud VM, `uv sync`.
- For each template: `verity_numerical.bench.lowerings.registry("C-Flock").module(t).frame_lowering(TM.subcircuit(...))`, then `low.layout.counts`.
- For sampling: `verity_flock.ir_sampling.lane(128256)`.
- For attention: `module("attention-head").lowering(sc, T)`.

| template | units per VU | ANDs per unit | rows per unit | ANDs per VU | verifier-evaluated tail (IR gates) | public cut words |
|---|---|---|---|---|---|---|
| rope-head D=64 | 32 | 5,996 | 6,273 | 191,872 | 0 | 0 |
| silu-mul I=8192 | 4,096 | 5,398 | 5,761 | 22,110,208 | 0 | 0 |
| rmsnorm-fused-cuda N=2048 | 32 | 317,334 | 325,761 | 10,154,688 | 36 | 33 |
| rmsnorm-triton N=2048 | 8 | 1,132,502 | 1,147,009 | 9,060,016 | 18 | 9 |
| attention-head T=4 | 80 | 8,623 | — | 689,840 | 224 | 217 |
| attention-head T=129 | 1,092 | 8,623 | — | 9,416,316 | 1,046 | 1,543 |
| sampling lane (V=128,256) | 128,256 | 5,099 | — | 6.54e8 | row scalars, top-p word, per-lane carries (all public) | — |

**Attention.** A head has 4T + 64·⌈T/16⌉ tensor-core steps, 8,623 ANDs each. Summed over T=1..287, 16 layers and 32 heads, that is 173.7 M steps, or 1.50e12 ANDs.

**GEMM.** One coordinate is K/16 steps: 8,623 ANDs each with the generic lowering, 7,100 with the census unit (binary-backend census).

**Pieces, for scale:**

| piece | ANDs |
|---|---|
| f32 add | 823 |
| f32 mul | 2,406 |
| f32 fma | 4,498 |
| bf16 × bf16 mul | 741 |
| 16-bit lookup with 32-bit output | 3,256 |

**#101 total:** about 1.57e14 ANDs. The non-GEMM templates are about 1.75e12.

## C-Flock phase shares on the L40S

Source: the render's Table 3, `renders/daily/20260926T1548Z-tables.json`.

| template | witness | arithmetic | encoding + commitment |
|---|---|---|---|
| RMSNorm fused | 86% | 3% | 0% |
| RMSNorm Triton | 87% | 2% | 0% |
| RoPE d64 | 70% | 7% | 0% |
| SiLU·mul | 83% | 4% | 0% |
| top-p | 83% | 27% (interaction reads −23%) | 1% |
| attention, per T | 57–82% | 4–11% | — |
| GEMM K=8192 | 25% | 46% | 8% |
| GEMM K=2048 | 26% | — | 8% |

**H100 prover-only** (`lanes/flock-ir-lowering/evidence/20260926T0435Z-h100-ir-block-all4.json`, flock-ir-block/v1, both reps). GPU prove took:
- 0.49 s for 256 RMSNorm-fused rows (2.6e9 ANDs), which is 5.3 G AND/s;
- 0.059 s for 1,024 RoPE heads, 3.3 G AND/s;
- 0.153 s for 32 SiLU rows, 4.6 G AND/s.

Host witness generation took 4.9 of the 5.5 s end to end.

## Projection model (`/tmp/proj2.py`, reproduced here)

**Inputs** come from #101's `workload_headline`: per-template native seconds on the headline basis, and C-Flock L40S proving seconds.
- Attention is extrapolated from its covered 164 T values in proportion to native seconds: 4,571 s × 6.313 / 2.6745 ms, which gives 10,791 s.
- Top-p is at the published 5.5e6×, which is 52 s for 32 rows.

**The ZK escape hatch, on today's prover:**

~~~text
t_zk = t_now × AND_factor × (w + (1 − w)(1 + z))
~~~

- w is the witness share (L40S Table 3).
- z is 0.03, 0.10 or 0.30: the ZK tax on the proving share.
- AND_factor is 8,623/7,100 for GEMM (the generic unit), 1.28 for attention (softmax in the circuit), 1.01 for RMSNorm (row tail), 2 for top-p (the top-p word in the circuit) and 1 otherwise.

**With GPU witness generation:** the witness term becomes w/20 on the non-GEMM templates, and GEMM is left unchanged.

**Results.** Headline native basis 8.476 ms; all-memory-bound basis 0.6728 s.

| scenario | L40S-seconds | headline basis | memory-bound basis |
|---|---|---|---|
| C-Flock today, extrapolated to full coverage | 51,306 | 6.05e6× | 7.63e4× |
| ZK escape hatch, today's prover | 63,987 – 74,550 (central 66,726) | 7.55e6 – 8.79e6× | 9.5e4 – 1.1e5× |
| ZK escape hatch + GPU witness | 53,144 – 63,708 (central 55,883) | 6.27e6 – 7.52e6× | 7.9e4 – 9.5e4× |
| + the 7,100-AND census unit for GEMM | 46,829 | 5.52e6× | 6.96e4× |
| B-Ligero for GEMM + escape hatch for the rest | 105,921 | 1.25e7× | 1.57e5× |

**GEMM share.** GEMM is 91.7% of the central GPU-witness scenario.

**B-Ligero ratios.** The last row applies the H100 ratios of B-Ligero to C-Flock on the same statement: 2.14 at K=2048 (1.2e8 / 5.6e7) and 3.75 at K=8192 (1.8e8 / 4.8e7).

Other published B-Ligero to C-Flock ratios on the same statement and SKU:

| statement | ratio |
|---|---|
| K=1536 H100 BF16 | 1.33 |
| K=1536 H100 FP8 | 1.47 |
| K=1536 H100 FP8, vllm-v1 | 1.95 |
| K=1536 4090 FP8 | 1.31 |

## Why no pod run

The $10 option was not used. Table 3 above and the H100 relation-only file already split the generic-netlist prover from witness generation, and that split is what a new run would have measured.

**The measurement worth doing next** belongs to M0, not to scoping: generic-netlist GPU witness generation on an L40S. It would check the assumed 20× speedup on the witness share.
