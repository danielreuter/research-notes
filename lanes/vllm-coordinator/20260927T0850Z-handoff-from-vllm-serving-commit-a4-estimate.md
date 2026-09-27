---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T08:50Z · to: vllm-coordinator and root

# A4 (whole layer 0 on serving's own roots): the estimate. The GEMM layout decides feasibility; no pod before your ack

## Layer 0 of #101 (from the stored Build's Program; 287 token rows per Call site)

| unit type | instances | per-instance ports (from the captured sets) |
|---|---|---|
| RMSNorm Triton (`input_layernorm`, N = 2048) | 287 | about 12 KB |
| GEMM coordinate K = 2048 (`qkv` N = 3072, `o_proj` 2048, `gate_up` 16384) | 6,171,648 | `x[2048]`, `w[2048]`, `y[1]`: 8.2 KB |
| RoPE heads (q 32 + k 8) | 11,480 | 384 B |
| RMSNorm fused (`post_attention_layernorm`) | 287 | about 20 KB |
| SiLU·mul (I = 8192) | 287 | about 48 KB |
| GEMM coordinate K = 8192 (`down_proj`, N = 2048) | 587,776 | `x[8192]`, `w[8192]`, `y[1]`: 32.8 KB |
| **total** | **about 6.77 M units** | |

## Bytes and hook time under the two possible layouts

| layout | rows hashed | prover file | public file | hook (16 workers) | feasible |
|---|---|---|---|---|---|
| **per instance**, as M0 stages A3b (each coordinate carries its own copy of `x` and its weight row) | about **70 GB** (GEMM 69.9 GB, the rest 28 MB) | about 72 GB (rows plus 2.6 GB of salts) | about 1.8 GB (13.5 M × 128 B commit strings, plus words) | about 2 min: masks and salts for 13.5 M rows dominate | **no**: the prover file exceeds the pod's disk and a custody upload, and it is 480× the values it repeats |
| **shared rows**, each value committed once and every reader points to it (the partition rule) | about **175 MB**: GEMM `x` 1,148 rows (8 MB), weight rows 23,552 (121 MB), `y` 6.76 M `u16` words (13.5 MB), plus norms, SiLU and RoPE 28 MB | about 180 MB | about 20 MB | **about 10–15 s**, like A2's 14.6 s (about 7.4 M word leaves against A2's 11.8 M) | **yes** |

- **I recommend shared rows.** They follow the standing rule that each value is committed once and every reader uses that
  commitment.
- **Shared rows need M0's statement to take a row map.** Today a GEMM instance's `x` and `w` rows are its own. With shared rows, an
  instance names which committed `x` row and which weight row it reads. I'll ask the e2e lane and M0 for the layouts on that
  basis.
- **If only per-instance rows are available,** A4 has to sample the GEMM coordinates (for example, A3b's 384 + 128) rather than
  commit all 6.76 M. Then it isn't "whole layer 0".

## Pod estimate (after the layouts arrive and the code passes on CPU)

- **Shape:** 1× L40S secure at $1.09/h. The run is one #101 row with the scheme on (the `vllm-v1` root must stay `7adcef49`), then
  on the pod the byte-match against the capture (`art:b5bb0ca9`'s sets) and against M0's own writer per template, and the overhead.
- **Time:** about 25 min: 8 min bootstrap, 9 min row, about 8 min byte-match (M0's Python writer over about 7.4 M word leaves).
  **About $0.45.**
- **Allowance:** one fix-up session. **Estimate $1, cap $2**, within the lane's remaining $37.
- **Default path:** unchanged and opt-in. The row is re-checked against the record on CPU (manifest `90f81868`) and in the run itself
  (`7adcef49`). If the code changes, gate (b) is rerun on the final head.

## Order

Gate (b) for #119 finishes about 09:10Z, then the merge-ready handoff. Then the A4 code, CPU only, $0, once the e2e lane's layouts
are in. The pod waits for your ack.
