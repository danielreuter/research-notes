---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: proofs · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · to: @proofs (bc-8416bc72) · created: 2026-09-30T20:55Z

# M0's state: `flock-m0-v3` at 4.80e6 prefill / 1.04e5 decode; one bench in flight, no new work taken

**The line.**
- Metric: GEMM proving overhead, prover s ÷ native bf16 GEMM s, Llama-3.2-1B, RTX PRO 6000, campaign `overnight-sep30`.
- Line `flock-m0-v3`, on branch `cursor/ov-gemm-slowdown-4d6a`, draft [PR #554](https://github.com/danielreuter/verity/pull/554).
- Best: #19 `r20260930-181717-b71e`, 4.82e6 / 1.04e5; #20 `r20260930-184956-61fe`, 4.80e6 / 1.05e5.
- Start: v1 #0, 3.48e7 / 7.91e5.
- Every attempt is byte-identity gated (GPU proofs = the CPU prover's) and labelled with its GPU.

**What moved it tonight**, all with the same bytes:

| Attempt | Change | Result |
|---|---|---|
| #13 | 4×4 tiles at m = 35 | |
| #15 | ring switch rewritten | 0.095 to 0.034 s a rep |
| #17 | lincheck quirky eq factored; SHA tape a thread per compression | |
| #19 | rep 0's witness kept inside the arena (`FC_KEEP_EXTRA_W`, default now 0) | rep 1 reuses it at m = 35 |
| #20 | `fc_sha_rows` word cache | |

**Measured and not kept:**

| Attempt | Change | Result |
|---|---|---|
| #14 | chunked device prefetch | slower than its same-job control |
| #16 | copy-engine staging of the host slots | a loss at the tile, reverted |
| #21 | zerocheck kernels at 2 blocks an SM | slower, reverted |

**In flight: #22, the last of the `provers` benches.**
- It carries two changes: compression rows pinned during the host prebuild (`99788b1b`), and Ligerito level 0's OOD eq table as halves (`cuda_circuit_patch.py`).
- Its same-job control switches both off: `FC_ROWS_PINNED=0 FC_LIG_EQ_FULL=1`.
- It's waiting to enter Kueue: 22 jobs were waiting at 20:50Z. A tmux loop on my VM retries every 3 min for up to 3 h.
- I'll label it and add its result here when it lands.

**I'm taking no new backlog work** unless you assign it. The remaining levers are:
- inside upstream Flock kernels: the zerocheck (28% of a statement), Ligerito (26%) and the NTT;
- or statement changes, which are Daniel's decisions:
  - packed unit slots, which would let K = 8,192 tile 2×2 in a 2^26 block;
  - a denser SHA slot;
  - K_MAX 27.
- The 4×4 tile layout still needs a statement and pin review before any pinned use.

**Notes:**
- Morning-report inputs: `lanes/flock-netlist/20260930T1235Z-report-prover-morning-inputs.md`.
- Nsight tables: `lanes/flock-v2-design/20260930T1110Z-handoff-from-flock-netlist-nsys-m35.md`, with a fresh profile at run `r20260930-155032-45bb`.
