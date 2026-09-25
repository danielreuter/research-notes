---
id: vllm-rf-c1/state
lane: vllm-rf-c1
kind: state
agent: bc-9eae5bc7 (Cursor), coordinator bc-ba6cec03
created: 2026-09-25T06:52Z
updated: 2026-09-25T07:26Z
---
# vllm-rf-c1: C1, commitment scheme vllm-v1 (named-scheme form)

Deadline for vyv- pods: 2026-09-25T09:00Z (coordinator extends). Budget: $35 pod spend.

## Status
- Phase 1 (evidence only, no repo commits): started 06:52Z.
  - PR #15 (`fa9c4594`) is in `origin/main` (`00ffe398`, "Merge #15"). A4 (`lane/vllm-rf-a4`) is not yet in main.
  - Source for pod runs: clean detached worktree `~/projects/verity-wt/rf-c1-p1` at `00ffe398`.
- Phase 2: waiting for A4 in main.

## Pods
- `vyv-rf-c1-g1` (runpod `zaazjzf44rc4wr`), 1x L40S, CUDA 12.9/13.0 allowed, created 07:07Z, guard 90.
  - Bootstrap run `r20260925-070509-d288`: BOOTSTRAP-OK.

## Phase 1 plan
1. CUDA SHA-256 copies vs `vllm-v1` vectors on the L40S (the FA3 tap does no hashing, so no H100).
   Driver: `evidence/pod-scripts/cuda_vectors.py`.
2. Weights root on a live model (Llama-3.2-1B, `bi-eager`, the regression row #101 model) through
   `NativeHostCommitter.register_weights()` (host, device, device-checked) vs the core `vllm-v1`
   reference, plus row #101's recorded Commit weights root. Driver: `evidence/pod-scripts/weights_root.py`.

## Running
- `r20260925-072432-1077` on vyv-rf-c1-g1: weights_root.py `--case LLAMA32_1B --execution bi-eager --records /workspace/c1/records-101` (launched 07:24Z).

## Results
### Phase 1.1: CUDA SHA-256 copies vs `vllm-v1` vectors: ALL EQUAL (run `r20260925-072312-94f5`, fetched + preserved)
Evidence: `evidence/cuda_vectors.r20260925-072312-94f5.json` (vectors.json sha256 `f63cd95d…`). L40S sm_89, torch 2.13.0+cu129,
vLLM 0.28.1rc1.dev472, nvcc 12.4. Driver `evidence/pod-scripts/cuda_vectors.py`. Result: `CUDA-VECTORS-OK`, 0 mismatches.

| copy | how it was run | equal | covered vectors |
|---|---|---|---|
| `native_tree.cu` (production .so) | ctypes on the extern "C" launchers of the JIT-built `verity_native_collect.so` (sha256 `bee47f00…`) | 33/33 | chunk_leaf 0–2 (whole step + ci_base window), trees N=1–17 (root + every path), node, lift, run-root fold ×2, weights-root fold |
| `native_tree.cu` (standalone) | `nvcc -O3 --use_fast_math -arch=sm_89` | 33/33 | same |
| `hidden_gpu_tree.cu` | production `hidden_gpu.ext()` | 30/30 | chunk_leaf 0–2, trees N=1–17 (root + paths), node, lift (via 3-leaf `tree_levels`), run-root fold ×2, weights-root fold |
| `native_leafhash.cu` | production `leafhash.ext()` | 45/45 | pos_leaf len 1–4096 (single + tail after 256/4096 leaves), trees N=1–17, node, weights-root fold |
| `verity_tap.h` (H1, VERITY_TAP=4) | harness TU per src_mask over the tap8 FA2 tree | 3/3 | thread_leaf 0–2 (src_mask 1, 27, 16) |

Not covered, by construction: chunk_leaf[3] (BN/D = 64/128; the chunk kernels hard-wire header words 8/9 to 0, as PROTOCOL §6 says);
the empty tree, `empty/v1`, `leaf/v1` and every root's binding (host code); pos_leaf len 0 (`pos_leaves` refuses it; the host skips numel 0).
The first attempt `r20260925-071724-fd55` failed only because the H1 harness lacked FA2's global `using namespace cute;` (harness bug,
fixed; A–C were already all equal there).

## Found, not fixed
- thread_leaf[1] (src_mask 27) carries ok0 = 1 where the kernel constructor derives 0 for its (m_block, seqlen_q). The digest still
  matches (the header encodes the bits given), but the vector is a field combination the tap never emits. Vector-generation note, not a
  CUDA defect.
- The pod's nvcc is 12.4 while torch is cu129; every JIT extension above (production path) was built by that nvcc.
