---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T05:58Z · re: the boundary check on every row

# Boundary check complete on all 13 rows: #39 is affected too (pre-bias qkv Gemm), #11 is clean. #39 needs a decision

**#11 and #39**, by streaming the first 60,000 rows of each row's single request Program (layer 0 whole, layer 1 in part).
- Method: notes `evidence/s1_prefix_cb.py`, validated on #23, #57 and #74, where it reproduces their known results. Output: `evidence/s1_prefix_11_39.json`.

| Row | Extra Values in the prefix | What |
|---|---:|---|
| #11 | 0 | clean |
| **#39** | **6,752** | `Gemm_v1` under `qkv_proj`: the pre-bias output, read by `BiasAdd_v1` in the same module. One per token per layer |

**All 13 rows:**
- Clean: #4, #11, #23, #60, #67, #68, #70, #73, #75 and #101.
- Need a source: **#57** (Gemma's norm chain), **#74** (`Fp8GroupQuant` x_q / x_s) and **#39** (the pre-bias qkv Gemm).

**#39 under S1b (host evaluation). Your call:**
- The producer reads only committed values (the norm output and `qkv_proj.weight`), so option 1 applies as decided.
- The cost is the whole qkv GEMM on the host, exactly: K = 1536, N = 2048 (the q, k and v heads), 96 tensor-core steps per coordinate, over 4,608 tokens and 28 layers. That's about **25 G exact k16 steps per Commit**, which could add tens of minutes of host time per pair on the pod, depending on how fast the numpy kernel runs.
- **Alternatives:**
  - (a) Capture the pre-bias tensor where the runtime already has it. vLLM's batch-invariant path runs the bias add after the matmul, so it is exact and costs nothing. But it's a tap, not host evaluation.
  - (b) Restate `Gemm_v1` + `BiasAdd_v1` as one Definition, so the pre-bias value becomes interior to each coordinate unit. That moves #39's Definitions.
- **My recommendation:** hold #39 with #57 and #74 until S1b. Take (a) if the host path measures too slow once S1b is up. I'll time the host kernel on CPU first.

**S1b status:** being built in a worktree: `cursor/epoch-s1b-host-boundaries-150d`, stacked on S1. It covers #57 and #74 and exposes x_s for S4's `scale_products`. Target: merge-ready well before 12:30Z.
