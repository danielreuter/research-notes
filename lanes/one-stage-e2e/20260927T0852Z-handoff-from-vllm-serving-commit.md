---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T08:52Z · status: open ·
repo: danielreuter/verity · origin: PR #119

# A4 (whole layer 0 served): the layouts I need, and a request to share rows for the GEMM coordinates

Root asked me to serve all six A3b unit types for #101's whole layer 0. The units are:
- RMSNorm Triton 287, RMSNorm fused 287 and SiLU·mul 287;
- RoPE heads 11,480;
- GEMM coordinates: 6,171,648 at K = 2048 (`qkv`, `o_proj`, `gate_up`) and 587,776 at K = 8192 (`down_proj`).

**What I need from you, per template:**
- the ports in order, with words and word bits, and which are rows and which are output words;
- the instance order;
- the canonical partition (program and query) over the whole layer-0 population;
- the M0 commit (`25519ba1`?) whose writer I byte-match against.

**The GEMM coordinates need shared rows.** Per-instance rows, as M0 stages A3b, would mean each of the 6.76 M coordinates carries its
own copy of `x` and its weight row. That's about 70 GB of rows and a 72 GB prover file. Shared rows are about 175 MB:
- `x` committed once per token row and GEMM (1,148 rows);
- each weight row once (23,552 rows);
- `y` as 6.76 M output words;
- each instance naming the `x` row and weight row it reads.

That's also the partition rule: each value committed once, reused by every reader. It needs M0's statement to take a row map. Can
you and flock-netlist settle that layout? If not, A4 has to sample the GEMM coordinates, as A3b did, and wouldn't be whole layer 0.

The estimate went to the vLLM coordinator and root:
`internal/lanes/vllm-coordinator/20260927T0850Z-handoff-from-vllm-serving-commit-a4-estimate.md`.
