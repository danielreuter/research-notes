---
id: 20261001T1440Z-report-from-circuits-grid-models-counts-0740
campaign: overnight-sep30
lane: circuits
kind: report
status: done
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (7:40 AM PDT): counts for the 7:50 check

These counts come from the labeller's gather at 14:37Z, on both nodes since the grid began at 08:21Z. Every number below is a
`cov-gm*` item of mine (`labeller/counts_nodes.py`, `labeller/counts.py`).

**Deployments ended: 134**, with 127 passing and 7 failing. Every failure has a named cause.

- Where they ran, Build / Commit:
  - node 1 / node 1: 104
  - node 2 / node 1: 26 (Builds moved by `n2_build`)
  - node 1 / node 2: 3
  - node 2 / node 2: 1
- Commits on node 2 replayed there (`.n2-replay` rc 0); every other replay ran on node 1.
- Of the ended deployments, 9 are the golden twins (all unpacked; `note:20261001T1355Z-finding-golden-twins-unpacked-all-match`).
- Still in flight: 15. Submitted so far: 149 (74 on `cursor-grid-models-8c79`, the rest on the plan and
  boundary trees).

**Models: 19 with an ended deployment, 18 with a pass. Families: 9, all 9 with a pass** (falcon3, llama3, mistral, olmoe, phi,
qwen25, qwen3, smollm2, yi). gemma2-9b, the tenth family, is held: no Gemma-2 from me, per your 07:49Z ruling.

| Model | Family | Pass | Fail |
| --- | --- | --- | --- |
| falcon3-1b | falcon3 | 8 | 0 |
| falcon3-7b | falcon3 | 4 | 0 |
| llama31-8b | llama3 | 6 | 0 |
| llama32-3b | llama3 | 10 | 0 |
| mistral-7b-instruct | mistral | 6 | 0 |
| olmoe-1b-7b-0125-instruct | olmoe | 6 | 0 |
| phi4-14b | phi | 6 | 0 |
| qwen25-05b-instruct | qwen25 | 15 | 0 |
| qwen25-3b | qwen25 | 8 | 0 |
| qwen25-coder-15b | qwen25 | 8 | 0 |
| qwen3-06b | qwen3 | 4 | 5 |
| qwen3-14b | qwen3 | 4 | 0 |
| qwen3-17b | qwen3 | 8 | 0 |
| qwen3-30b-a3b-2507 | qwen3 | 0 | 1 |
| qwen3-8b | qwen3 | 3 | 1 |
| r1-distill-llama-8b | llama3 | 4 | 0 |
| r1-distill-qwen-15b | qwen25 | 8 | 0 |
| smollm2-17b | smollm2 | 10 | 0 |
| yi15-6b | yi | 9 | 0 |

**Failures by named cause**

- **6: a Definition gap, SiluMul_v1's expf-overflow edge. Not a Commit fault.**
  - Items: cov-gm001, 031, 081, 082 and 001-pk (qwen3-06b), and cov-gm149 (qwen3-8b, B8 256 stochastic, new this hour).
  - For a gate at or below -89, the GPU's silu gives -0, while SiluMulBf16_v1 gives a tiny g·e^g.
  - At every mismatched element, the quarantined SiluMul_v2 equals the committed word (`labeller/silu_check.py`).
- **1: a configuration error in my item. Not a Commit fault.**
  - cov-gm127 (qwen3-30b-a3b-2507, B1 256) set no GPU_UTIL, so row.py's default `gpu_memory_utilization` of 0.5 applied.
  - That is below the model's 56.9 GiB of weights at TP1, so vLLM's KV cache came to -9.81 GiB and the Commit died 43 s in.
  - The same model passed at 0.9 (cov-g172). The 11 unsubmitted qwen3-30b-a3b-2507 items now set `GPU_UTIL=0.9`.
  - Because of this, qwen3-30b-a3b-2507 has no pass yet. cov-gm137, its B8 256 row, is in flight with the fix.

**Since 7:12 AM PDT:** the deadline gate is gone, per your 1412Z ruling. The estimate order and the burst caps stay. Build
concurrency is now bound by `deployments-cpu`'s memory quota: 480 Gi nominal plus 128 Gi of borrowing, against Build requests of
86–128 GB each. My FINAL follows by 7:50.

