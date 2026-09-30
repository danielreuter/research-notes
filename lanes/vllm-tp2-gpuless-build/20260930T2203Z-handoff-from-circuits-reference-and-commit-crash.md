---
id: 20260930T2203Z-handoff-from-circuits-reference-and-commit-crash
campaign: verity
lane: vllm-tp2-gpuless-build
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# @circuits: a GPU-visible TP2 Build to compare against may already exist (cov-p002-2); and TP2's Commit crashes too (NCCL P2P?)

1. **Reference Build:** `cov-p002-2` ran a GPU-visible 2-rank Build of `llama32-1b__bf16__rtxpro6000__tp2__b1__i1024__o128__mixed__greedy__bi-eager`
   on node 1 (passed in 955 s, word check passed; run `r20260930-212250-262e`, row dir `/workspace/jobs/cov/cov-p002-2/<row>/`, tree
   `cursor-coverage-v0-2622`). If your CPU-only Build (`r20260930-212809-14a0`) is the same row, and your tree differs only in the
   platform selection, compare digests against it now instead of waiting for a 2-GPU admission. If the trees differ in anything that
   moves digests, keep your reference job; I've asked @infra to admit it at the front.
2. **The Commit crashes on sm_120 at TP2:** `cov-p002-2`'s Commit failed after 68 s, rank 1 `CUDA error: an illegal memory access`
   (`commit.log` in the same row dir). Node 1's `config-run-row.yaml` doesn't set `NCCL_P2P_DISABLE=1`, which TP2 on these GPUs (no
   NVLink) needs. Pending the research owner's yes, your acceptance should include one TP2 Commit of that row with `NCCL_P2P_DISABLE=1`
   (question: does TP2's Commit run on sm_120 without P2P?), and the `config-run` template's 2-GPU Commit should set it.

Results to `lanes/circuits/`.
